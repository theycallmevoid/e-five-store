# E Five Store

Django storefront with editable products, galleries, tracking pixels, orders, and ZR Express settings.

## Local setup

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `/admin/` to manage the store. ZR Express credentials are stored in the Django database under **ZR Express settings** and are never committed to Git.

## Render

- Build command: `bash build.sh`
- Start command: `gunicorn efive.wsgi:application --bind 0.0.0.0:$PORT`
- Set `DATABASE_URL` to an IPv4-compatible Supabase Session Pooler URI.
