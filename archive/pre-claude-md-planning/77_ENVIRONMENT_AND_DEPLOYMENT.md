# 77_ENVIRONMENT_AND_DEPLOYMENT

## Purpose

Defines local, staging, and production deployment requirements.

---

## Local Development

Required:
- Node.js
- Python or backend runtime
- PostgreSQL
- package manager
- `.env`

---

## Environment Variables

### Frontend

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Backend

```env
DATABASE_URL=postgresql://user:password@localhost:5432/evercrafted
JWT_SECRET=replace-me
AI_API_KEY=server-side-only
CORS_ORIGINS=http://localhost:3000
```

---

## Staging

Recommended:
- Vercel preview frontend
- Render/Railway backend staging
- Supabase/Neon staging database

---

## Production

Recommended:
- Vercel frontend
- Render/Railway backend
- Supabase/Neon PostgreSQL
- Cloudflare R2 for future storage
- Sentry for errors
- PostHog for product analytics

---

## Security Rules

- Never expose AI API key to browser.
- Use HTTPS in production.
- Enforce user ownership on all records.
- Validate all blueprint JSON before saving.
