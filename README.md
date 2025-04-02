# Prometheus Bot

A sophisticated trading and content generation platform combining algorithmic trading with AI-powered content creation.

## Features

### Trading Engine
- Multi-timeframe analysis for crypto and stocks
- Advanced risk management system
- Real-time market data processing
- Multiple strategy support
- Performance analytics

### Content Generation
- AI-powered trading reports
- Market analysis content
- Social media updates
- Email newsletters
- Performance summaries

### Web Platform
- Next.js dashboard
- Real-time trading interface
- Content management system
- Performance analytics
- User authentication

## Architecture

- **API**: FastAPI backend
- **Database**: PostgreSQL with SQLAlchemy
- **Cache**: Redis
- **Frontend**: Next.js with v0 functions
- **Monitoring**: Prometheus & Grafana
- **Queue**: Redis pub/sub
- **Container**: Docker & Docker Compose

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/prometheus-bot.git
cd prometheus-bot
```

2. Set up environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start services with Docker:
```bash
docker-compose up -d
```

4. Initialize database:
```bash
docker-compose exec api alembic upgrade head
```

5. Access services:
- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

## Development Setup

1. Create Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Set up web platform:
```bash
cd web-platform
npm install
npm run dev
```

3. Start development services:
```bash
# Terminal 1: API
uvicorn api.main:app --reload

# Terminal 2: Trading Bot
python -m trading.main

# Terminal 3: Content Generation
python -m content.main
```

## Project Structure

```
prometheus-bot/
├── api/                # FastAPI application
├── trading/           # Trading engine
├── content/           # Content generation
├── web-platform/      # Next.js dashboard
├── database/          # Database models
├── core/              # Core functionality
├── tests/            # Test suite
├── docker/           # Docker configuration
├── alembic/          # Database migrations
├── scripts/          # Utility scripts
└── docs/             # Documentation
```

## Configuration

The application is configured through environment variables. See `.env.example` for all available options.

Key configuration areas:
- API settings
- Database connection
- Redis configuration
- Trading parameters
- Content generation
- Monitoring setup

## Testing

Run the test suite:
```bash
pytest
```

For coverage report:
```bash
pytest --cov=.
```

## Deployment

See `deployment_checklist.md` for detailed deployment instructions.

Key deployment steps:
1. Configure environment
2. Set up infrastructure
3. Deploy services
4. Initialize database
5. Configure monitoring
6. Verify functionality

## Monitoring

The application includes comprehensive monitoring:

- **Prometheus**: Collects metrics
- **Grafana**: Visualizes metrics
- **Logging**: Structured JSON logs
- **Alerts**: Email & Slack notifications

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository. 