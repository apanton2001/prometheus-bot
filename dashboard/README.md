# Dashboard Frontend

This directory contains the React frontend for the Prometheus Bot dashboard.

## Features

- Trading bot performance visualization
- Content management interface
- Service delivery dashboard
- Stock analysis visualization
- System configuration UI
- User authentication and management

## Setup

1. Install dependencies
   ```
   npm install
   ```

2. Configure environment
   ```
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

3. Start development server
   ```
   npm run dev
   ```

## Development

### Folder Structure
```
dashboard/
├── public/           # Static assets
├── src/
│   ├── components/   # Reusable React components
│   ├── pages/        # Page components
│   ├── hooks/        # Custom React hooks
│   ├── services/     # API services
│   ├── utils/        # Utility functions
│   ├── context/      # React contexts
│   ├── styles/       # Global styles
│   └── types/        # TypeScript definitions
└── tests/            # Component tests
```

### Available Scripts

- **npm run dev**: Start development server
- **npm run build**: Build production version
- **npm run start**: Start production server
- **npm run test**: Run tests
- **npm run lint**: Run linter

## Features

### Trading Dashboard
- Real-time performance metrics
- Trade history visualization
- Strategy configuration
- Risk management settings

### Content Manager
- Content creation interface
- Scheduling and distribution
- Content analytics
- Template management

### Service Dashboard
- Customer management
- Service delivery tracking
- Workflow visualization
- Support ticket management

### Stock Analysis
- Stock screening interface
- Analysis visualization
- Report generation
- Portfolio tracking

## Technologies

- React
- Next.js
- TypeScript
- Tailwind CSS
- Chart.js / D3.js
- React Query 