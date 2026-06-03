# irtibāṭ — Backend API

Django REST Framework backend for irtibāṭ, a smart bookmark manager.

🔗 **Live API:** [web-production-0939ea.up.railway.app/api](https://web-production-0939ea.up.railway.app/api/)  
💻 **Frontend Repo:** [github.com/Niyaso/irtibat-frontend](https://github.com/Niyaso/irtibat-frontend)

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login and get JWT tokens |
| POST | `/api/auth/refresh/` | Refresh access token |
| GET | `/api/auth/me/` | Get current user |
| GET/POST | `/api/bookmarks/` | List and create bookmarks |
| PATCH | `/api/bookmarks/:id/toggle-read/` | Toggle read status |
| GET | `/api/bookmarks/read-later/` | Get unread bookmarks |
| GET/POST | `/api/collections/` | List and create collections |
| GET/POST | `/api/tags/` | List and create tags |
| POST | `/api/quick-save/` | Save link via bookmarklet |
| GET | `/api/public/:username/:slug/` | Public collection (no auth) |

---

## Tech Stack

- **Django 6** + **Django REST Framework**
- **PostgreSQL** (production via Railway)
- **JWT Authentication** via djangorestframework-simplejwt
- **BeautifulSoup4** for URL metadata scraping (Open Graph)
- **Gunicorn** for production serving
- **dj-database-url** for database configuration

---

## Local Setup

```bash
git clone https://github.com/Niyaso/irtibat-backend.git
cd irtibat-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API available at `http://localhost:8000/api/`  
Admin panel at `http://localhost:8000/admin/`

---

## How the Scraper Works

When a bookmark is saved, the backend:
1. Sends a GET request to the URL
2. Parses the HTML with BeautifulSoup
3. Extracts Open Graph tags (`og:title`, `og:description`, `og:image`)
4. Falls back to `<title>` tag and meta description if OG tags are missing
5. Saves thumbnail URL, favicon URL, title and description automatically

---

## Deployment

- **Platform:** Railway
- **Database:** Railway PostgreSQL
- **Environment Variables:** `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`

---

## Author

**Muhammed Niyas**  
[github.com/Niyaso](https://github.com/Niyaso)
