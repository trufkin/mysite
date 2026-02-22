Deployment notes

This project uses gunicorn as the WSGI server. Example Procfile is included.

Environment variables to set in production:
- `DJANGO_SECRET_KEY` — set a secure secret key and update settings to read from env in production.
- `DATABASE_URL` — if using external DB (Postgres). Update `DATABASES` accordingly.
- `ALLOWED_HOSTS` — set to your hostnames.

Example (Heroku):
1. `git push heroku main`
2. `heroku config:set DJANGO_SECRET_KEY=...`
3. `heroku run python manage.py migrate`
4. `heroku ps:scale web=1`

For Docker or other platforms, run gunicorn: `gunicorn config.wsgi --bind 0.0.0.0:$PORT`.
