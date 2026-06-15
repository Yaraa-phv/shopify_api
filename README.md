# Shopify Clone API

A REST API for a Shopify-style e-commerce storefront, built with **FastAPI**, **async SQLAlchemy**, and **PostgreSQL**. It covers authentication, product catalog, collections, shopping cart, checkout, orders, reviews, and user profiles.

## Features

- **JWT authentication** — register, login, protected routes
- **User profile** — update profile, change password, manage shipping addresses
- **Products & categories** — CRUD (admin), public listing, search, filters
- **Collections** — curated product groups (e.g. "Summer Sale", "New Arrivals")
- **Shopping cart** — add, update, remove items; variant support (size/color)
- **Orders** — checkout from cart, order history, inventory deduction
- **Reviews** — product ratings and reviews (1–5 stars)
- **OpenAPI docs** — interactive Swagger UI at `/docs`

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI 0.111 |
| Server | Uvicorn |
| ORM | SQLAlchemy 2.0 (async) |
| Database driver | asyncpg |
| Database | PostgreSQL (local or [Neon](https://neon.tech)) |
| Auth | JWT (python-jose) + bcrypt |
| Validation | Pydantic v2 |
| Config | pydantic-settings |

## Project Structure

```
shopify_api/
├── app/
│   ├── main.py                 # App entry point, CORS, health check
│   ├── api/
│   │   ├── deps.py             # JWT auth, admin guard
│   │   └── v1/
│   │       ├── auth.py         # Register, login
│   │       ├── users.py        # Profile & addresses
│   │       ├── products.py     # Products, categories, reviews
│   │       ├── collections.py  # Collections
│   │       ├── cart.py         # Shopping cart
│   │       └── orders.py       # Checkout & orders
│   ├── core/
│   │   ├── config.py           # Environment settings
│   │   └── security.py         # Password hashing, JWT
│   ├── db/
│   │   ├── base.py             # SQLAlchemy declarative base
│   │   └── session.py          # Async engine & session
│   ├── models/                 # SQLAlchemy ORM models (12 tables)
│   ├── schemas/                # Pydantic request/response models
│   └── services/               # Business logic layer
├── scripts/
│   ├── schema.sql              # Full PostgreSQL schema
│   └── init_db.sql             # DB bootstrap notes
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## Database Schema

| Table | Description |
|-------|-------------|
| `users` | Accounts (email, password hash, role) |
| `categories` | Product categories |
| `products` | Product catalog |
| `product_variants` | Size/color variants with stock |
| `product_images` | Product image URLs |
| `addresses` | User shipping addresses |
| `cart` / `cart_items` | Per-user shopping cart |
| `orders` / `order_items` | Placed orders |
| `reviews` | Product reviews |
| `collections` / `collection_products` | Curated product groups |

Apply the schema with `scripts/schema.sql` in your PostgreSQL or Neon SQL editor.

## Prerequisites

- Python 3.11+
- PostgreSQL 14+ (local) or a [Neon](https://neon.tech) account
- Git

## Local Setup

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd shopify_api

python -m venv .venv

# Windows (Git Bash)
source .venv/Scripts/activate

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

If you hit SSL errors on Windows (Git Bash), use:

```bash
python -m pip install -r requirements.txt \
  --trusted-host pypi.org \
  --trusted-host files.pythonhosted.org
```

### 3. Configure environment variables

Create a `.env` file in the project root (see `.env.example`):

```env
APP_NAME=Shopify Clone API
DEBUG=false
API_V1_PREFIX=/api/v1

# Local PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/shopify_db

SECRET_KEY=your-long-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

DEFAULT_SHIPPING_COST=5.99
```

Generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Create the database

**Local PostgreSQL:**

```sql
CREATE DATABASE shopify_db;
```

Then run the contents of `scripts/schema.sql` against `shopify_db`.

**Neon (cloud):**

Use the connection string from the Neon dashboard, converted for async SQLAlchemy:

```
# Neon gives you:
postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require

# Use this in .env instead:
postgresql+asyncpg://user:pass@ep-xxx.neon.tech/neondb?ssl=require
```

Changes: `postgresql+asyncpg://`, `ssl=require`, remove `channel_binding=require`.

Run `scripts/schema.sql` in the Neon SQL editor (skip `CREATE DATABASE`).

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000 | API root |
| http://127.0.0.1:8000/docs | Swagger UI |
| http://127.0.0.1:8000/redoc | ReDoc |
| http://127.0.0.1:8000/health | Health check |

## API Endpoints

Base path: `/api/v1`

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register` | — | Create account |
| `POST` | `/auth/login` | — | Login, returns JWT |
| `GET` | `/auth/me` | Bearer | Current user |

### User Profile

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/users/me` | Bearer | Get profile |
| `PUT` | `/users/me` | Bearer | Update profile |
| `PUT` | `/users/me/password` | Bearer | Change password |
| `GET` | `/users/me/addresses` | Bearer | List addresses |
| `POST` | `/users/me/addresses` | Bearer | Add address |
| `PUT` | `/users/me/addresses/{id}` | Bearer | Update address |
| `DELETE` | `/users/me/addresses/{id}` | Bearer | Delete address |

### Categories & Products

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/categories` | — | List categories |
| `GET` | `/categories/{id}` | — | Get category |
| `POST` | `/categories` | Admin | Create category |
| `PUT` | `/categories/{id}` | Admin | Update category |
| `GET` | `/products` | — | List products (`?search=`, `?category_id=`) |
| `GET` | `/products/{id}` | — | Product detail |
| `POST` | `/products` | Admin | Create product |
| `PUT` | `/products/{id}` | Admin | Update product |
| `DELETE` | `/products/{id}` | Admin | Delete product |
| `GET` | `/products/{id}/reviews` | — | List reviews |
| `GET` | `/products/{id}/rating` | — | Average rating |
| `POST` | `/products/{id}/reviews` | Bearer | Add review |

### Collections

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/collections` | — | List collections |
| `GET` | `/collections/slug/{slug}` | — | Collection by slug |
| `GET` | `/collections/{id}` | — | Collection by ID |
| `POST` | `/collections` | Admin | Create collection |
| `PUT` | `/collections/{id}` | Admin | Update collection |
| `DELETE` | `/collections/{id}` | Admin | Delete collection |

### Cart & Orders

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/cart` | Bearer | View cart |
| `POST` | `/cart/items` | Bearer | Add item |
| `PUT` | `/cart/items/{id}` | Bearer | Update quantity |
| `DELETE` | `/cart/items/{id}` | Bearer | Remove item |
| `DELETE` | `/cart` | Bearer | Clear cart |
| `GET` | `/orders` | Bearer | Order history |
| `GET` | `/orders/{id}` | Bearer | Order detail |
| `POST` | `/orders` | Bearer | Checkout (creates order from cart) |

## Authentication Guide

### Login

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "MySecurePass123"}'
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Use the token

```bash
curl http://127.0.0.1:8000/api/v1/auth/me \
  -H "Authorization: Bearer <your-token>"
```

### Swagger UI

1. Call `POST /api/v1/auth/login` to get a token.
2. Click **Authorize** (lock icon).
3. Paste the token in the **Value** field (no `Bearer ` prefix).
4. Click **Authorize** → **Close**.

### Create an admin user

Register normally, then in PostgreSQL:

```sql
UPDATE users SET role = 'admin' WHERE email = 'you@example.com';
```

Admin routes require `role = 'admin'`.

## Typical User Flow

1. **Register** → `POST /auth/register`
2. **Login** → `POST /auth/login` → save token
3. **Browse products** → `GET /products`
4. **Add to cart** → `POST /cart/items`
5. **Checkout** → `POST /orders`
6. **View orders** → `GET /orders`

## Deploy on Render

### 1. Push to GitHub

Ensure `.env` is **not** committed (it is listed in `.gitignore`).

### 2. Create a Web Service on Render

| Setting | Value |
|---------|-------|
| Runtime | Python 3 |
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### 3. Environment variables (Render dashboard)

| Variable | Example |
|----------|---------|
| `DATABASE_URL` | `postgresql+asyncpg://...@neon.tech/neondb?ssl=require` |
| `SECRET_KEY` | `<generated-random-hex>` |
| `DEBUG` | `false` |
| `CORS_ORIGINS` | `["https://your-frontend.onrender.com"]` |

### 4. Database

Use Neon (or Render PostgreSQL). Run `scripts/schema.sql` before first deploy.

### 5. Health check

Render can use `GET /health` as the health check path.

## Docker (optional)

```bash
docker build -t shopify-api .
docker run -p 8000:8000 --env-file .env shopify-api
```

For production, pass environment variables instead of baking `.env` into the image.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | Async PostgreSQL URL (`postgresql+asyncpg://...`) |
| `SECRET_KEY` | Yes | — | JWT signing secret |
| `APP_NAME` | No | `Shopify Clone API` | App title in docs |
| `API_V1_PREFIX` | No | `/api/v1` | API route prefix |
| `DEBUG` | No | `false` | SQLAlchemy query logging |
| `ALGORITHM` | No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `1440` | Token lifetime (24h) |
| `CORS_ORIGINS` | No | `localhost:3000,5173` | Allowed frontend origins |
| `DEFAULT_SHIPPING_COST` | No | `5.99` | Default shipping at checkout |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `psycopg2 is not async` | Use `postgresql+asyncpg://` in `DATABASE_URL`, not `postgresql://` |
| SSL cert error installing packages | Add `--trusted-host pypi.org --trusted-host files.pythonhosted.org` |
| `password cannot be longer than 72 bytes` | Fixed — app uses `bcrypt` directly (not `passlib`) |
| `Invalid email or password` | Login with plain text password, not a bcrypt hash string |
| Tables don't exist | Run `scripts/schema.sql` on your database |
| 403 on admin routes | Set `role = 'admin'` for your user in the DB |

## License

Academic / assignment project — adjust as needed for your course requirements.
