# Content Generation Bot

This directory contains the content generation system leveraging OpenAI's GPT models for creating blog posts, social media content, and marketing materials.

## Features

- Automated content generation for various platforms
- Content scheduling and distribution
- SEO optimization
- Performance analytics
- Multi-format outputs (blog posts, tweets, Instagram captions, etc.)

## Setup

1. Install dependencies
   ```
   pip install -r requirements.txt
   ```

2. Configure API keys
   ```
   cp .env.example .env
   # Add your OpenAI API key to .env
   ```

3. Configure content templates
   ```
   cp templates/config.example.json templates/config.json
   # Edit config.json with your content preferences
   ```

## Usage

### Generate Blog Post
```
python generate_content.py --type blog --topic "Trading Strategies" --length medium
```

### Generate Social Media Batch
```
python generate_content.py --type social-batch --topics "Trading,Crypto,Finance" --count 10
```

### Schedule Distribution
```
python schedule_content.py --config content_calendar.json
```

## Content Types

- **Blog Posts**: Long-form content (1000-2000 words)
- **Social Media**: Short-form content for Twitter, Instagram, etc.
- **Email Marketing**: Email newsletters and campaigns
- **Product Descriptions**: Descriptions for services and features

## Analytics

Use the analytics module to track content performance:
```
python analytics.py --timeframe 30d
``` 