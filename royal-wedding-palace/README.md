# Royal Wedding Palace

Full-stack wedding venue booking application built with Django REST Framework and React/TypeScript.

## Features
- Hall and package catalogue, images, menu and verified reviews
- User registration/login using Django REST Framework tokens
- Real database reservations, cost estimates, personal booking history
- Unique database constraint prevents two active bookings for the same hall/date
- Django staff administration for venues, date blocks, prices, bookings and testimonials
- Staff reporting API, availability calendar, optional Telegram notification
- Mobile-friendly black/gold interface; Uzbek, English and Russian UI toggle

## Run locally
Requirements: Python 3.11+, Node 20+. From this directory:

```bash
cd backend
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # on Windows: copy .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py test
python manage.py runserver
```

New terminal:
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and Django admin at http://localhost:8000/admin/.
API base: http://localhost:8000/api/

## Configuration / deployment
SQLite works out of the box; set DATABASE_URL=postgresql://USER:PASS@HOST:5432/DB for PostgreSQL. Create a unique Django SECRET_KEY; set DEBUG=0, ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS, CSRF_TRUSTED_ORIGINS and HTTPS before deployment. Set Telegram BOT_TOKEN and TELEGRAM_CHAT_ID for admin booking alerts; if absent, reservations still work. VITE_API_URL overrides API location.

*Demo photographs*: Unsplash-hosted images are linked remotely for the demo. Review the [Unsplash license](https://unsplash.com/license) and replace demo images with appropriately licensed business photographs before public launch. No images are re-distributed.

Bookings are real records; no payment gateway is integrated. Prices are estimates, not payments. Photos, business details, venue addresses and social links are demonstrative.

## API
POST /api/auth/register/, /api/auth/login/, /api/auth/logout/
GET /api/auth/me/
GET /api/halls/, /api/packages/, /api/menu/, /api/gallery/, /api/reviews/
GET /api/calendar/?hall=<id>&month=YYYY-MM
GET, POST /api/bookings/
POST /api/bookings/<id>/cancel/ (owner), /api/bookings/<id>/decide/ (staff)
GET /api/stats/ (staff only)

## Concurrency
Django's conditional database unique constraint is the final safeguard; create operations are wrapped in atomic transactions. On PostgreSQL, it protects even simultaneous reservations. Cancelled/rejected bookings release dates.

## Known production follow-ups
Add rate limiting/email verification, background notification delivery, structured audit logs, real payment provider and payment reconciliation, deployed object storage for uploads, localized server messages and end-to-end browser tests.
## Status
Source-code implementation; this repository has not yet passed an installed-dependency build, migrations run or end-to-end deployment validation. Generate initial migrations with `python manage.py makemigrations` before first `migrate`. Review and commit generated migration files before production deployment.
