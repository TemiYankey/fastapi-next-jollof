# FastAPI Next Jollof 🍛

A production-ready, battle-tested boilerplate for building full-stack applications with **FastAPI** (backend) and **Next.js** (frontend), with **Supabase** authentication that works without hydration issues.

## Features

### Backend (FastAPI)
- **Supabase JWT Authentication** - JWKS-based token validation with Redis caching
- **Tortoise ORM** - Async PostgreSQL with migrations (Aerich)
- **Redis Integration** - Session caching, rate limiting, JWKS caching
- **Rate Limiting** - SlowAPI with configurable limits per endpoint type
- **Production Logging** - Rotating file logs per component
- **Sentry Integration** - Error tracking (production only)

### Frontend (Next.js 14)
- **SSR-Safe Auth** - No hydration issues with Supabase
- **Recovery Session Detection** - Proper password reset flow
- **Protected Routes** - Easy-to-use route protection
- **Zustand State** - Global user state management
- **React Query** - Server state with smart caching
- **Tailwind CSS** - Dark mode support with CSS variables
- **Sonner Toasts** - Beautiful notifications

### Auth Features
- Email/Password login
- Google OAuth
- Email confirmation
- Password reset
- Session management
- Auto-logout on token expiration

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL
- Redis
- Supabase project

### 1. Clone & Setup

```bash
cd fastapi-next-jollof
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your values

# Initialize database migrations
aerich init -t app.core.database.TORTOISE_ORM
aerich init-db

# Run the server
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
# Edit .env.local with your values

# Run development server
npm run dev
```

### 4. Supabase Setup

1. Create a project at [supabase.com](https://supabase.com)
2. Go to Settings > API and copy:
   - Project URL → `SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_URL`
   - `anon` public key → `SUPABASE_PUBLIC_KEY` / `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`
   - `service_role` secret → `SUPABASE_SECRET_KEY`
   - JWT Secret → `SUPABASE_JWT_SECRET`

3. Enable Email Auth in Authentication > Providers
4. (Optional) Enable Google OAuth in Authentication > Providers

## Project Structure

```
fastapi-next-jollof/
├── backend/
│   ├── app/
│   │   ├── base/           # Base models, schemas, utilities
│   │   ├── core/           # Config, database, redis, logging
│   │   ├── users/          # Auth routes, models, JWT decoder
│   │   └── main.py         # FastAPI app entry
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── auth/           # Auth pages (signin, signup, etc.)
│   │   ├── (dashboard)/    # Protected routes
│   │   └── providers.tsx   # App providers
│   ├── components/
│   │   ├── auth/           # Auth components
│   │   └── ui/             # UI components
│   ├── contexts/           # AuthContext
│   ├── stores/             # Zustand stores
│   ├── utils/api/          # API client
│   └── .env.example
│
└── README.md
```

## Configuration

### Backend Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_JWT_SECRET` | Supabase JWT secret | Yes |
| `SECRET_KEY` | App secret key | Yes |
| `CORS_ALLOWED_ORIGINS` | Comma-separated origins | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `SENTRY_DSN` | Sentry DSN (production) | No |

### Frontend Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_APP_NAME` | App display name | No |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | Yes |
| `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | Supabase anon key | Yes |
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |

## Customization

### App Name
Update in both environments:
- Backend: `APP_NAME` in `.env`
- Frontend: `NEXT_PUBLIC_APP_NAME` in `.env.local`

### Theme Colors
Edit `frontend/app/globals.css` to customize:
- Light/dark mode colors via CSS variables
- Primary brand color

### Adding Features
The auth system is modular. Add new features by:
1. Creating models in `backend/app/<feature>/models.py`
2. Adding routes in `backend/app/<feature>/routes.py`
3. Including router in `backend/app/main.py`
4. Creating API calls in `frontend/utils/api/<feature>.ts`

## Auth Flow

### Sign In
1. User submits email/password
2. Supabase validates credentials
3. Frontend calls `/api/auth/me` with token
4. Backend creates/fetches user from DB
5. User data stored in Zustand

### Protected Routes
```tsx
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

export default function MyPage() {
  return (
    <ProtectedRoute>
      <YourProtectedContent />
    </ProtectedRoute>
  );
}
```

### Using Auth
```tsx
import { useAuth } from "@/contexts/AuthContext";
import { useUserStore } from "@/stores/userStore";

function Component() {
  const { isAuthenticated, logout } = useAuth();
  const { user } = useUserStore();

  return <div>Hello, {user?.fullName}</div>;
}
```

## Production Deployment

### Backend
1. Set `ENVIRONMENT=production`
2. Configure Sentry DSN
3. Use production database
4. Deploy with Gunicorn + Uvicorn workers

### Frontend
1. Build with `npm run build`
2. Deploy to Vercel/similar
3. Set production environment variables

## Acknowledgments

This boilerplate is based on patterns from [Writera](https://github.com/your-writera-project) - a production application that has battle-tested these auth patterns.

## License

MIT License - Use this boilerplate for any project!
