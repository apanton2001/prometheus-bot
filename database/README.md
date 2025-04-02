# Database Module

This directory contains the database schemas and migrations for the Prometheus Bot project.

## Features

- PostgreSQL database integration
- SQLAlchemy ORM models
- Alembic migrations
- Connection pooling
- Data access layer

## Setup

1. Install PostgreSQL
   ```
   # On Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib
   
   # On macOS with Homebrew
   brew install postgresql
   
   # On Windows, download from https://www.postgresql.org/download/windows/
   ```

2. Create database and user
   ```
   # Login to PostgreSQL
   sudo -u postgres psql
   
   # Create database and user
   CREATE DATABASE prometheus;
   CREATE USER prometheus_user WITH ENCRYPTED PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE prometheus TO prometheus_user;
   ```

3. Configure database connection
   ```
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. Run migrations
   ```
   alembic upgrade head
   ```

## Database Schema

- **users**: User accounts and authentication
- **trading_bots**: Trading bot configurations
- **strategies**: Trading strategies
- **trades**: Trade history and performance
- **content**: Generated content
- **services**: Service delivery
- **stock_analysis**: Stock analysis data

## Migrations

Run migrations with Alembic:

```
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Backup and Restore

### Backup
```
pg_dump -U prometheus_user -d prometheus -f backup.sql
```

### Restore
```
psql -U prometheus_user -d prometheus -f backup.sql
```

## Access Patterns

Use the data access layer for database operations:

```python
from database.access import TradingBotDAO

# Get a bot by ID
bot = TradingBotDAO.get_by_id(bot_id)

# Create a new bot
new_bot = TradingBotDAO.create(name="My Bot", strategy="EMA Cross", user_id=user_id)
``` 