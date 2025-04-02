import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'workflow.log'))
    ]
)

logger = logging.getLogger("WorkflowManager")

class WorkflowStep:
    """
    A single step in a workflow.
    """
    def __init__(self, step_id, name, action, params=None, next_steps=None, on_error=None):
        self.step_id = step_id
        self.name = name
        self.action = action
        self.params = params or {}
        self.next_steps = next_steps or []
        self.on_error = on_error
        
    def execute(self, context):
        """
        Execute the workflow step.
        
        Args:
            context (dict): The workflow context
            
        Returns:
            tuple: (success, updated_context)
        """
        logger.info(f"Executing step: {self.name} (ID: {self.step_id})")
        
        try:
            # Execute the action
            action_result = self.action(context, **self.params)
            
            # Update the context with the action result
            if isinstance(action_result, dict):
                context.update(action_result)
            
            logger.info(f"Step {self.name} completed successfully")
            return True, context
        except Exception as e:
            logger.error(f"Error executing step {self.name}: {str(e)}")
            
            if self.on_error:
                logger.info(f"Executing error handler for step {self.name}")
                try:
                    self.on_error(context, error=str(e))
                except Exception as err:
                    logger.error(f"Error in error handler: {str(err)}")
            
            return False, context

class Workflow:
    """
    A workflow consisting of multiple steps.
    """
    def __init__(self, workflow_id, name, steps=None, context=None):
        self.workflow_id = workflow_id
        self.name = name
        self.steps = steps or {}
        self.context = context or {}
        self.start_step = None
        
    def add_step(self, step):
        """
        Add a step to the workflow.
        
        Args:
            step (WorkflowStep): The step to add
        """
        self.steps[step.step_id] = step
        
    def set_start_step(self, step_id):
        """
        Set the starting step for the workflow.
        
        Args:
            step_id (str): The ID of the starting step
        """
        if step_id not in self.steps:
            raise ValueError(f"Step with ID {step_id} not found in workflow")
        
        self.start_step = step_id
        
    def execute(self, initial_context=None):
        """
        Execute the workflow from the start step.
        
        Args:
            initial_context (dict): Initial context to use
            
        Returns:
            dict: The final workflow context
        """
        if not self.start_step:
            raise ValueError("No start step defined for workflow")
        
        # Initialize the workflow context
        context = self.context.copy()
        if initial_context:
            context.update(initial_context)
        
        # Add workflow execution metadata
        context["workflow_id"] = self.workflow_id
        context["workflow_name"] = self.name
        context["execution_id"] = f"{self.workflow_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        context["start_time"] = datetime.now().isoformat()
        
        logger.info(f"Starting workflow: {self.name} (ID: {self.workflow_id})")
        
        # Start executing from the start step
        current_step_id = self.start_step
        
        while current_step_id:
            # Get the current step
            current_step = self.steps.get(current_step_id)
            
            if not current_step:
                logger.error(f"Step with ID {current_step_id} not found in workflow")
                break
            
            # Execute the step
            success, context = current_step.execute(context)
            
            # Determine the next step
            if success and current_step.next_steps:
                # Get the next step based on conditions
                for next_step in current_step.next_steps:
                    if "condition" not in next_step or next_step["condition"](context):
                        current_step_id = next_step["step_id"]
                        break
                else:
                    # No matching condition found, end the workflow
                    current_step_id = None
            else:
                # No next steps or step failed, end the workflow
                current_step_id = None
        
        # Add workflow completion metadata
        context["end_time"] = datetime.now().isoformat()
        
        logger.info(f"Workflow {self.name} completed")
        
        return context

class WorkflowManager:
    """
    Manager for loading, executing, and tracking workflows.
    """
    def __init__(self, workflows_dir=None):
        self.workflows = {}
        self.workflows_dir = workflows_dir or os.path.join(os.path.dirname(__file__), "definitions")
        
    def load_workflow(self, workflow_id):
        """
        Load a workflow from its definition file.
        
        Args:
            workflow_id (str): The ID of the workflow to load
            
        Returns:
            Workflow: The loaded workflow
        """
        workflow_path = os.path.join(self.workflows_dir, f"{workflow_id}.json")
        
        if not os.path.exists(workflow_path):
            raise FileNotFoundError(f"Workflow definition not found: {workflow_path}")
        
        with open(workflow_path, "r") as f:
            definition = json.load(f)
        
        # Create a new workflow instance
        workflow = Workflow(
            workflow_id=workflow_id,
            name=definition.get("name", workflow_id),
            context=definition.get("context", {})
        )
        
        # TODO: Load steps from definition
        # This is simplified and would need to be expanded to map actions to actual functions
        
        self.workflows[workflow_id] = workflow
        return workflow
        
    def execute_workflow(self, workflow_id, context=None):
        """
        Execute a workflow.
        
        Args:
            workflow_id (str): The ID of the workflow to execute
            context (dict): Initial context to use
            
        Returns:
            dict: The final workflow context
        """
        # Load the workflow if not already loaded
        if workflow_id not in self.workflows:
            self.load_workflow(workflow_id)
        
        workflow = self.workflows[workflow_id]
        return workflow.execute(context)
        
    def list_workflows(self):
        """
        List all available workflows.
        
        Returns:
            list: List of workflow IDs
        """
        # List all JSON files in the workflows directory
        if not os.path.exists(self.workflows_dir):
            return []
        
        return [
            os.path.splitext(f)[0]
            for f in os.listdir(self.workflows_dir)
            if f.endswith(".json")
        ]

# Example usage
if __name__ == "__main__":
    # Define some example actions
    def send_welcome_email(context, template=None):
        print(f"Sending welcome email to {context.get('email')} using template {template}")
        return {"email_sent": True, "email_template": template}
    
    def create_user_account(context, role=None):
        print(f"Creating user account for {context.get('name')} with role {role}")
        return {"account_created": True, "user_role": role}
    
    def provision_resources(context, resource_type=None, quantity=1):
        print(f"Provisioning {quantity} {resource_type} for user {context.get('name')}")
        return {"resources_provisioned": True, "resource_type": resource_type, "quantity": quantity}
    
    # Create workflow steps
    step1 = WorkflowStep(
        step_id="welcome_email",
        name="Send Welcome Email",
        action=send_welcome_email,
        params={"template": "welcome_basic"},
        next_steps=[{"step_id": "create_account"}]
    )
    
    step2 = WorkflowStep(
        step_id="create_account",
        name="Create User Account",
        action=create_user_account,
        params={"role": "basic_user"},
        next_steps=[{"step_id": "provision_resources"}]
    )
    
    step3 = WorkflowStep(
        step_id="provision_resources",
        name="Provision User Resources",
        action=provision_resources,
        params={"resource_type": "storage", "quantity": 5}
    )
    
    # Create the workflow
    workflow = Workflow(
        workflow_id="user_onboarding",
        name="User Onboarding Workflow"
    )
    
    # Add steps to the workflow
    workflow.add_step(step1)
    workflow.add_step(step2)
    workflow.add_step(step3)
    
    # Set the starting step
    workflow.set_start_step("welcome_email")
    
    # Execute the workflow
    result = workflow.execute({
        "name": "John Doe",
        "email": "john.doe@example.com"
    })
    
    print("Workflow result:", result) 