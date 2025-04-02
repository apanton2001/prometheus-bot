# Prometheus Bot API

This directory contains the FastAPI backend for the Prometheus Bot.

## Features

- REST API for trading bot control and monitoring
- WebSocket support for real-time updates
- Authentication and authorization
- Rate limiting
- Swagger documentation

## Setup

1. Install dependencies
   ```
   pip install -r requirements.txt
   ```

2. Configure environment variables
   ```
   cp .env.example .env
   ```

3. Run development server
   ```
   uvicorn main:app --reload
   ```

## API Endpoints

- `/api/v1/auth` - Authentication endpoints
- `/api/v1/trading` - Trading bot control
- `/api/v1/content` - Content generation
- `/api/v1/service` - Service automation
- `/api/v1/stock-analysis` - Stock analysis 