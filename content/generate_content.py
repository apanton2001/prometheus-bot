#!/usr/bin/env python3
"""
Content generation script using OpenAI GPT models.
"""
import argparse
import json
import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OpenAI API key not found. Please set it in the .env file.")
    sys.exit(1)

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate content using OpenAI GPT models')
    
    parser.add_argument('--type', type=str, required=True,
                        choices=['blog', 'tweet', 'social-batch', 'email', 'product'],
                        help='Type of content to generate')
    
    parser.add_argument('--topic', type=str,
                        help='Main topic for the content')
    
    parser.add_argument('--topics', type=str,
                        help='Comma-separated list of topics for batch generation')
    
    parser.add_argument('--length', type=str, default='medium',
                        choices=['short', 'medium', 'long'],
                        help='Length of the generated content')
    
    parser.add_argument('--count', type=int, default=1,
                        help='Number of pieces to generate for batch mode')
    
    parser.add_argument('--template', type=str,
                        help='Template file to use')
    
    parser.add_argument('--output', type=str, default='./output',
                        help='Directory to save the generated content')
    
    parser.add_argument('--model', type=str, default='gpt-4-turbo-preview',
                        help='OpenAI model to use')
    
    return parser.parse_args()

def load_template(content_type: str, template_file: Optional[str] = None) -> Dict:
    """
    Load content template from file or use defaults.
    
    Args:
        content_type: Type of content to generate
        template_file: Optional path to template file
        
    Returns:
        Template dictionary with prompts and parameters
    """
    if template_file and os.path.exists(template_file):
        with open(template_file, 'r') as f:
            return json.load(f)
    
    # Default templates
    templates = {
        "blog": {
            "prompt": "Write a comprehensive blog post about {topic}. The tone should be professional and informative, targeting an audience interested in finance and trading. Include relevant statistics, examples, and actionable insights. Structure the post with clear headings and subheadings.",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "tweet": {
            "prompt": "Write an engaging tweet about {topic} that would appeal to traders and investors. Include relevant hashtags and a clear call to action.",
            "temperature": 0.9,
            "max_tokens": 280,
        },
        "social-batch": {
            "prompt": "Write a social media post about {topic} for {platform}. The tone should be {tone} and it should include a call to action.",
            "temperature": 0.8,
            "max_tokens": 500,
        },
        "email": {
            "prompt": "Write an email newsletter about {topic} for subscribers interested in trading and investment strategies. Include a compelling subject line, an engaging introduction, valuable content in the body, and a clear call to action.",
            "temperature": 0.6,
            "max_tokens": 1500,
        },
        "product": {
            "prompt": "Write a compelling product description for {topic}. Highlight its key features, benefits, and why it's valuable for traders and investors. Include technical specifications where relevant and end with a call to action.",
            "temperature": 0.5,
            "max_tokens": 1000,
        }
    }
    
    if content_type not in templates:
        logger.error(f"Unknown content type: {content_type}")
        sys.exit(1)
        
    return templates[content_type]

def generate_content(
    prompt: str,
    model: str = "gpt-4-turbo-preview",
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> str:
    """
    Generate content using OpenAI GPT models.
    
    Args:
        prompt: Prompt to send to the model
        model: OpenAI model to use
        temperature: Temperature for generation (0.0 to 1.0)
        max_tokens: Maximum tokens to generate
        
    Returns:
        Generated content as string
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional content creator specializing in finance, trading, and investment topics."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return ""

def save_content(content: str, content_type: str, topic: str, output_dir: str) -> str:
    """
    Save generated content to file.
    
    Args:
        content: Generated content
        content_type: Type of content
        topic: Topic of the content
        output_dir: Directory to save the content
        
    Returns:
        Path to the saved file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a filename based on content type, topic, and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_topic = topic.lower().replace(" ", "_").replace(",", "")
    filename = f"{content_type}_{sanitized_topic}_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)
    
    # Save content to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

def main():
    """Main function."""
    args = parse_args()
    
    # Load template
    template = load_template(args.type, args.template)
    
    # Process based on content type
    if args.type == "social-batch":
        if not args.topics:
            logger.error("For social-batch type, --topics argument is required")
            return 1
            
        topics = [topic.strip() for topic in args.topics.split(',')]
        platforms = ["Twitter", "LinkedIn", "Facebook", "Instagram"]
        tones = ["informative", "persuasive", "enthusiastic", "professional"]
        
        results = []
        for _ in range(args.count):
            for topic in topics:
                # Select platform and tone
                import random
                platform = random.choice(platforms)
                tone = random.choice(tones)
                
                # Format prompt
                prompt = template["prompt"].format(
                    topic=topic,
                    platform=platform,
                    tone=tone
                )
                
                # Generate content
                content = generate_content(
                    prompt=prompt,
                    model=args.model,
                    temperature=template["temperature"],
                    max_tokens=template["max_tokens"]
                )
                
                if content:
                    # Save content
                    filepath = save_content(
                        content=content,
                        content_type=f"{args.type}_{platform.lower()}",
                        topic=topic,
                        output_dir=args.output
                    )
                    
                    results.append({
                        "topic": topic,
                        "platform": platform,
                        "filepath": filepath
                    })
                    
                    logger.info(f"Generated {platform} post about {topic}, saved to {filepath}")
        
        logger.info(f"Generated {len(results)} social media posts")
        
    else:
        if not args.topic:
            logger.error(f"For {args.type} type, --topic argument is required")
            return 1
        
        # Adjust max tokens based on length
        length_multipliers = {
            "short": 0.5,
            "medium": 1.0,
            "long": 1.5
        }
        max_tokens = int(template["max_tokens"] * length_multipliers[args.length])
        
        # Format prompt
        prompt = template["prompt"].format(topic=args.topic)
        
        # Generate content
        content = generate_content(
            prompt=prompt,
            model=args.model,
            temperature=template["temperature"],
            max_tokens=max_tokens
        )
        
        if content:
            # Save content
            filepath = save_content(
                content=content,
                content_type=args.type,
                topic=args.topic,
                output_dir=args.output
            )
            
            logger.info(f"Generated {args.type} about {args.topic}, saved to {filepath}")
        else:
            logger.error("Failed to generate content")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 