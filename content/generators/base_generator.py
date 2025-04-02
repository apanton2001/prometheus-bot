from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
import openai
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

class BaseGenerator(ABC):
    """
    Base class for all content generators.
    Defines the interface that all generators must implement.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the content generator with configuration parameters.
        
        Args:
            config (Dict): Generator configuration parameters
        """
        self.config = config
        self.model = ChatOpenAI(
            model_name=config.get('model_name', 'gpt-4'),
            temperature=config.get('temperature', 0.7),
            max_tokens=config.get('max_tokens', 2000)
        )
        
    @abstractmethod
    def generate_content(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        Generate content based on the provided prompt and context.
        
        Args:
            prompt: The main prompt for content generation
            context: Additional context for generation
            
        Returns:
            Generated content
        """
        pass
    
    @abstractmethod
    def validate_content(self, content: str) -> bool:
        """
        Validate if generated content meets quality criteria.
        
        Args:
            content: Generated content to validate
            
        Returns:
            True if content is valid, False otherwise
        """
        pass
    
    def format_prompt(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        Format the prompt with context for better generation.
        
        Args:
            prompt: Base prompt
            context: Additional context
            
        Returns:
            Formatted prompt
        """
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            return f"{prompt}\n\nContext:\n{context_str}"
        return prompt
    
    def get_system_message(self) -> str:
        """
        Get the system message for content generation.
        
        Returns:
            System message defining the generator's role
        """
        return """You are an expert content generator specializing in financial and market analysis.
        Your content should be informative, accurate, and engaging while maintaining a professional tone."""
    
    def generate_with_retry(self, prompt: str, context: Optional[Dict] = None, max_retries: int = 3) -> str:
        """
        Generate content with retry logic for validation failures.
        
        Args:
            prompt: Base prompt
            context: Additional context
            max_retries: Maximum number of retry attempts
            
        Returns:
            Validated generated content
            
        Raises:
            Exception: If content generation fails after max retries
        """
        formatted_prompt = self.format_prompt(prompt, context)
        
        for attempt in range(max_retries):
            try:
                messages = [
                    SystemMessage(content=self.get_system_message()),
                    HumanMessage(content=formatted_prompt)
                ]
                
                response = self.model(messages)
                content = response.content
                
                if self.validate_content(content):
                    return content
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Content generation failed after {max_retries} attempts: {str(e)}")
                    
        raise Exception("Failed to generate valid content after maximum retries")
    
    def get_metrics(self) -> Dict:
        """
        Get content generation performance metrics.
        
        Returns:
            Dict: Generator metrics including:
                - total_generations: int
                - successful_generations: int
                - failed_generations: int
                - average_length: float
                - average_generation_time: float
        """
        return {
            'total_generations': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'average_length': 0.0,
            'average_generation_time': 0.0
        } 