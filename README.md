# mysite

Development notes

- Python: >=3.12
- Use the project's virtualenv: `source .venv/bin/activate`
- Install dependencies: `poetry install` or `pip install -r requirements.txt` (this project uses Poetry).
- Run migrations: `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`
- Start dev server: `python manage.py runserver`

Admin: http://127.0.0.1:8000/admin/

CI Status

![Python Django Tests](https://github.com/your-org/your-repo/actions/workflows/python-tests.yml/badge.svg)
