# create-jollof-app

Create a full-stack FastAPI + Next.js application with authentication, payments, and more.

```
       ██╗ ██████╗ ██╗     ██╗      ██████╗ ███████╗
       ██║██╔═══██╗██║     ██║     ██╔═══██╗██╔════╝
       ██║██║   ██║██║     ██║     ██║   ██║█████╗
  ██   ██║██║   ██║██║     ██║     ██║   ██║██╔══╝
  ╚█████╔╝╚██████╔╝███████╗███████╗╚██████╔╝██║
   ╚════╝  ╚═════╝ ╚══════╝╚══════╝ ╚═════╝ ╚═╝
```

## Quick Start

```bash
npx create-jollof-app my-app
```

Or with options:

```bash
npx create-jollof-app my-app --theme emerald --payment stripe --email resend
```

## Interactive Mode

Just run without arguments for the full interactive experience:

```bash
npx create-jollof-app
```

You'll be prompted to choose:
- **Project name** - Your app's name
- **Color theme** - Brand color (indigo, violet, blue, emerald, rose, amber, cyan, orange)
- **Payment provider** - Nomba, Stripe, or Paystack
- **Email provider** - Resend, Brevo, or none
- **Git init** - Initialize a git repository
- **Install deps** - Install dependencies automatically

## Options

| Option | Description |
|--------|-------------|
| `-t, --theme <theme>` | Color theme (indigo, violet, blue, emerald, rose, amber, cyan, orange) |
| `-p, --payment <provider>` | Payment provider (nomba, stripe, paystack) |
| `-e, --email <provider>` | Email provider (resend, brevo, none) |
| `--frontend-port <port>` | Frontend port (default: 3000) |
| `--backend-port <port>` | Backend port (default: 8000) |
| `--no-git` | Skip git initialization |
| `--no-install` | Skip dependency installation |
| `-h, --help` | Display help |
| `-V, --version` | Display version |

## What's Included

### Backend (FastAPI)
- FastAPI with async Tortoise ORM
- Supabase authentication integration
- Payment processing (Nomba, Stripe, Paystack)
- Email service (Resend, Brevo)
- Rate limiting with SlowAPI
- Redis caching
- Comprehensive test suite (pytest)
- Tortoise CLI migrations

### Frontend (Next.js 15)
- Next.js 15 with React 19
- Supabase Auth with SSR
- TanStack Query for data fetching
- Zustand state management
- Tailwind CSS with customizable theme
- Vitest testing suite
- TypeScript throughout

### Features
- Google OAuth sign-in
- Email/password authentication
- Protected routes
- User profiles
- Credits-based billing
- Payment history
- Dark mode support

## After Creation

```bash
cd my-app

# Set up environment variables
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env

# Start frontend (Terminal 1)
cd frontend && npm run dev

# Start backend (Terminal 2)
cd backend && source venv/bin/activate && uvicorn app.main:app --reload
```

## Running Tests

### Frontend Tests
```bash
cd frontend
npm test
```

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

## Color Themes

| Theme | Preview | Best For |
|-------|---------|----------|
| Indigo | Professional & trustworthy | B2B, Finance |
| Violet | Creative & modern | Creative tools, Design |
| Blue | Classic & reliable | General purpose |
| Emerald | Fresh & growth-focused | Health, Finance, Growth |
| Rose | Bold & energetic | Consumer apps, Social |
| Amber | Warm & inviting | Food, Hospitality |
| Cyan | Tech & futuristic | Tech, AI, Startups |
| Orange (Jollof) | Vibrant & appetizing | Food, Energy |

## Requirements

- Node.js 18+
- Python 3.10+
- PostgreSQL (or Supabase)
- Redis

## License

MIT
