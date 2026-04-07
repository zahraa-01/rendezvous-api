# Rendezvous Backend API

## Overview
Rendezvous is a location-sharing application where users can discover, create, and manage places with authentic stories from locals and travellers.

## Tech Stack
- Django REST Framework
- JWT authentication (Simple JWT)
- SQLite / PostgreSQL-ready configuration
- SendGrid for email delivery
- Cloudinary for media uploads

## Features
- User authentication (register, login, JWT tokens)
- Places CRUD operations
- Image uploads for places and user profile avatars
- Search and filtering by city/country
- Owner-based permissions (users can only edit/delete their own places)
- User profile management (bio, location, avatar)
- SendGrid integration for email delivery (with console fallback in development)

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/token/` - Login (JWT tokens)
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/user/` - Current user info

### Places
- `GET /api/places/` - List places (supports search, city/country filtering)
- `POST /api/places/` - Create new place (auth required)
- `GET /api/places/{id}/` - Get place details
- `PATCH /api/places/{id}/` - Update place (owner only)
- `DELETE /api/places/{id}/` - Delete place (owner only)

### Profiles
- `GET /api/profile/` - Get current user profile
- `PATCH /api/profile/` - Update current user profile

## Setup Instructions

1. **Clone and set up environment**
```bash
git clone https://github.com/zahraa-01/rendezvous-api.git
cd rendezvous-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

2. **Configure environment variables**
Update the `.env` file with your own values.

3. **Database setup**
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Run server**
```bash
python manage.py runserver
```

## Environment Variables

Example `.env.example`:

```
# Django settings
SECRET_KEY=your_secret_key_here
DEBUG=True

# PostgreSQL
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

# SendGrid
SENDGRID_API_KEY=your_sendgrid_api_key
EMAIL_FROM=your_verified_email@example.com
```

## Known Issues & Development Notes

### Email Delivery
SendGrid integration is implemented and requests successfully reach the provider, but email delivery was blocked in development due to sender authentication restrictions and provider security rules. For local development and demo reliability, the project can use Django's console email backend so email content and templates can still be demonstrated in the terminal.

### Pagination
The Places API uses pagination (100 items per page) to keep list responses manageable while still allowing the frontend to display all available places across pages.

## Deployment Notes
- Use PostgreSQL for production
- Set DEBUG=False in production
- Configure proper CORS settings for the frontend domain
- Ensure Cloudinary is configured for media uploads
- Ensure SendGrid sender authentication is configured correctly for production email delivery

## AI Assistance Disclaimer
AI tools were used selectively during development to support parts of the UI design, README drafting, debugging, and troubleshooting. This was especially helpful when investigating SendGrid delivery issues and exploring password reset implementation. All final integration, testing, and implementation decisions were reviewed and validated within the project context.
