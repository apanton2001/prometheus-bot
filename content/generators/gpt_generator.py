import os
from pathlib import Path
import json
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class ContentGenerator:
    """
    Content generator using OpenAI GPT models to create various types of content.
    """
    
    def __init__(self, model="gpt-3.5-turbo"):
        """
        Initialize the content generator.
        
        Args:
            model (str): The GPT model to use for generation.
        """
        self.model = model
        
    def load_template(self, template_name):
        """
        Load a content template from the templates directory.
        
        Args:
            template_name (str): Name of the template file (without extension)
            
        Returns:
            dict: Template data
        """
        templates_dir = Path(__file__).resolve().parent.parent / "templates"
        template_path = templates_dir / f"{template_name}.json"
        
        with open(template_path, "r") as f:
            return json.load(f)
            
    def generate_content(self, template_name, variables=None):
        """
        Generate content based on a template.
        
        Args:
            template_name (str): Name of the template to use
            variables (dict): Variables to substitute in the template
            
        Returns:
            str: Generated content
        """
        template = self.load_template(template_name)
        prompt = template["prompt"]
        
        # Replace variables in prompt if provided
        if variables:
            for key, value in variables.items():
                prompt = prompt.replace(f"{{{key}}}", value)
        
        messages = [
            {"role": "system", "content": template.get("system_prompt", "You are a professional content creator.")},
            {"role": "user", "content": prompt}
        ]
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            max_tokens=template.get("max_tokens", 1000),
            temperature=template.get("temperature", 0.7)
        )
        
        return response.choices[0].message.content
        
    def generate_batch(self, template_name, variables_list):
        """
        Generate multiple content pieces using the same template.
        
        Args:
            template_name (str): Name of the template to use
            variables_list (list): List of variable dictionaries
            
        Returns:
            list: List of generated content pieces
        """
        return [self.generate_content(template_name, variables) for variables in variables_list]
        
    def generate_social_post(self, topic, platform="twitter", tone="professional"):
        """
        Generate a social media post.
        
        Args:
            topic (str): The topic of the post
            platform (str): The social media platform
            tone (str): The tone of the post
            
        Returns:
            str: Generated social media post
        """
        variables = {
            "topic": topic,
            "platform": platform,
            "tone": tone
        }
        
        return self.generate_content("social_post", variables)
        
    def generate_blog_article(self, title, keywords=None, word_count=800):
        """
        Generate a blog article.
        
        Args:
            title (str): The title of the article
            keywords (list): Keywords to include
            word_count (int): Target word count
            
        Returns:
            str: Generated blog article
        """
        variables = {
            "title": title,
            "keywords": ", ".join(keywords) if keywords else "",
            "word_count": str(word_count)
        }
        
        return self.generate_content("blog_article", variables) 