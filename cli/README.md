# create-jollof-app 🍛

A CLI to scaffold production-ready **FastAPI + Next.js** applications with authentication, payments, and email built-in.

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
npx create-jollof-app
```

Follow the interactive prompts to configure your app (name, theme, payment provider, etc.)

**Or use CLI flags:**

```bash
npx create-jollof-app my-app --theme emerald --payment nomba --email resend
```

## What You Get

### Backend (FastAPI)
- **Supabase Auth** - JWT validation with JWKS caching
- **Tortoise ORM** - Async PostgreSQL with built-in migrations
- **Payment Processing** - Nomba (tested), Stripe, Paystack
- **Email Service** - Resend or Brevo with templating
- **Rate Limiting** - SlowAPI with Redis
- **Redis Caching** - Sessions, JWKS, rate limits
- **Production Logging** - Rotating file logs
- **Test Suite** - pytest with async support

### Frontend (Next.js 15)
- **SSR-Safe Auth** - No hydration issues
- **React 19** - Latest features
- **TanStack Query** - Smart data fetching
- **Zustand** - Lightweight state management
- **Tailwind CSS** - Customizable themes + dark mode
- **TypeScript** - Full type safety

### Features
- Email/password + Google OAuth
- Protected routes
- User profiles
- Credits-based billing
- Payment history
- Docker setup (optional)

## CLI Options

| Option | Description |
|--------|-------------|
| `--type <type>` | Project type: fullstack, backend, frontend |
| `-t, --theme <theme>` | Color: indigo, violet, blue, emerald, rose, amber, cyan, orange |
| `-p, --payment <provider>` | Payment: nomba, stripe, paystack |
| `-e, --email <provider>` | Email: resend, brevo, none |
| `--frontend-port <port>` | Frontend port (default: 3000) |
| `--backend-port <port>` | Backend port (default: 8000) |
| `--no-git` | Skip git initialization |
| `--no-install` | Skip dependency installation |

## After Scaffolding

### 1. Set Up Environment Variables

```bash
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env
```

Edit both files with your Supabase, payment, and email credentials.

### 2. Set Up Supabase

1. Create a project at [supabase.com](https://supabase.com)
2. Copy your project URL, anon key, service role key, and JWT secret
3. Enable Email Auth in Authentication > Providers
4. (Optional) Enable Google OAuth

### 3. Start Development

**Option A: Docker (recommended)**
```bash
docker compose up -d
```

**Option B: Manual**
```bash
# Terminal 1 - Backend
cd backend
make install  # Creates venv and installs deps
make run      # Starts server

# Terminal 2 - Frontend
cd frontend
make install  # If you skipped install during scaffolding
make dev      # Starts server
```

### 4. Initialize Database

```bash
cd backend
source venv/bin/activate
tortoise init
tortoise makemigrations
tortoise migrate
```

Or use the Makefile:
```bash
make db-init     # Initialize
make migration   # Create migration
make migrate     # Apply migrations
```

## Running Tests

```bash
# Frontend
cd frontend && npm test

# Backend
cd backend && make test
```

## Color Themes

| Theme | Best For |
|-------|----------|
| Indigo | B2B, Finance, Professional |
| Violet | Creative tools, Design |
| Blue | General purpose |
| Emerald | Health, Finance, Growth |
| Rose | Consumer apps, Social |
| Amber | Food, Hospitality |
| Cyan | Tech, AI, Startups |
| Orange | Food, Energy, Vibrant |

## Requirements

- Node.js 18+
- Python 3.11+
- PostgreSQL (or use Docker)
- Redis (or use Docker)
- Supabase project

## Project Structure

```
my-app/
├── backend/
│   ├── app/
│   │   ├── base/        # Base models, utilities
│   │   ├── billing/     # Payments, plans, credits
│   │   ├── core/        # Config, database, redis
│   │   ├── emails/      # Email service + templates
│   │   └── users/       # Auth, profiles
│   ├── tests/
│   ├── Makefile
│   └── requirements.txt
├── frontend/
│   ├── app/             # Next.js pages
│   ├── components/      # React components
│   ├── contexts/        # Auth context
│   ├── stores/          # Zustand stores
│   └── utils/api/       # API client
├── docker-compose.yml
└── .gitignore
```

## License

MIT
