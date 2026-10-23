# DriveWise — Car Dealership Review Application

**IBM Full-Stack Software Developer Capstone coursework implementation.**

DriveWise is a functional local demonstration of a dealership review platform with a
Django website, a React frontend, Django JSON APIs, a separate optional Express
service, an SQLite database, Django administration, and GitHub Actions tests.

> **Important:** This is a development/coursework demonstration. All preloaded
> dealerships, addresses, reviews, and support contacts are fictional. The
> sentiment classifier is a simple keyword demonstration, not an ML model.
> IBM Cloud deployment, Kubernetes, and production authentication hardening are
> not included. MongoDB is used by the separate Express service only when a
> `MONGODB_URI` is configured; otherwise it uses clearly labeled sample data.

## What you can do

- Browse and filter dealerships by U.S. state.
- View individual dealership details and existing sample reviews.
- Register, sign in/out and publish reviews as an authenticated user.
- Manage dealership, vehicle make/model and review records in Django admin.
- Query APIs for dealerships, reviews, vehicle makes/models and sentiment.
- Run a React interface with the same Django API.
- Run a separate Express API with optional MongoDB persistence.
- Trigger GitHub Actions to run automated Django and React checks.

## Quick start (Windows 10/11)

1. Extract the provided DriveWise OneClick ZIP to a folder (not inside GitHub).
2. Double-click **`RUN_AND_PUSH.bat`** in the extracted top-level folder.
3. It clones your existing public GitHub repository, copies these sources, installs
   Django, makes migrations, creates the local database and fictional demo data,
   executes tests, commits and pushes a new commit to `main`.
4. When Git asks to authenticate, sign in to the GitHub account that owns the repo.
5. The script starts a Django console window. Open <http://127.0.0.1:8000/>.

Preconditions: **Python 3.10+**, **Git for Windows**, access to PyPI/GitHub. Node.js
is optional for using the Django server alone but needed for React/Express. The
script checks the build if Node/npm are installed. The script does **not** force
push or rewrite GitHub history. If dependency installation or tests fail, it
stops before committing and prints the problem.

## Run locally (after setup)

| Launcher | What it does | URL |
| --- | --- | --- |
| `RUN_SERVER.bat` | Start Django website and JSON APIs | http://127.0.0.1:8000/ |
| `RUN_REACT.bat` | Start React + Vite (Django must run too) | http://127.0.0.1:5173/ |
| `RUN_EXPRESS_API.bat` | Start optional Express API | http://127.0.0.1:3001/ |
| `COLLECT_EVIDENCE.bat` | Collect *real local cURL outputs* after starting Django | `.evidence/` |

Local demonstration credentials, **never for production**:

- Django web demo: `demo` / `DemoPass2026!` (or `DRIVEWISE_DEMO_PASSWORD` if set before initial seed).
- Django admin: `localadmin` / see local `.local_admin_credentials.txt`.
- To create your own admin: `python manage.py createsuperuser` inside the venv.

Never publish the SQLite database, local admin credentials, `.env`, or `.evidence`
files. They are in `.gitignore`.

## Repository layout

```text
manage.py                         Django entry point
server/settings.py                Django settings
server/urls.py                    Django routes
server/frontend/static/About.html   Course-required About Us page
server/frontend/static/Contact.html Course-required Contact Us page
server/frontend/src/components/Register/Register.jsx
server/frontend/src/App.jsx       Full React UI
microservices/dealer_api/         Optional Express + MongoDB microservice
dealership/models.py              Dealership/Review/CarMake/CarModel
 dealership/templates/dealership/ Django website templates
.github/workflows/django-ci.yml   Django tests and React build
scripts/collect_evidence.py       Capture local cURL outputs
```

## REST endpoints (Django port 8000)

| HTTP | Path | Purpose |
| --- | --- | --- |
| GET | `/api/dealerships/` | All dealers |
| GET | `/api/dealerships/1/` | Dealer details including reviews |
| GET | `/api/dealerships/state/KS/` | Kansas dealers |
| GET | `/api/reviews/dealer/1/` | Reviews for dealership 1 |
| GET | `/api/car-makes/` | Car makes and models |
| GET | `/api/sentiment/?text=Fantastic%20services` | Rule-based sentiment demonstration |
| GET | `/api/auth/csrf/` | Session CSRF token |
| GET | `/api/auth/me/` | Current session |
| POST | `/api/auth/login/` | Log in with JSON credentials and CSRF header |
| POST | `/api/auth/logout/` | Log out (CSRF header required) |
| POST | `/api/auth/register/` | Register with five fields |
| POST | `/api/reviews/` | Submit an authenticated review (CSRF required) |

Example real terminal commands (run after starting Django):

```bash
curl http://127.0.0.1:8000/api/dealerships/
curl http://127.0.0.1:8000/api/dealerships/state/KS/
curl http://127.0.0.1:8000/api/dealerships/1/
curl http://127.0.0.1:8000/api/reviews/dealer/1/
curl http://127.0.0.1:8000/api/car-makes/
curl 'http://127.0.0.1:8000/api/sentiment/?text=Fantastic%20services'
```

To get recorded actual requests and responses including session-based login/logout,
run `COLLECT_EVIDENCE.bat` while the Django server is running. The output files
are locally created under `.evidence/`, which Git ignores. If you use them as
course evidence, make sure the evaluator's prompt requests text, not images.

### Express/MongoDB service

If Node.js is installed, `RUN_EXPRESS_API.bat` starts an optional Express API on
port 3001. By default it returns explicitly fictional in-memory records. To use
actual MongoDB, configure `MONGODB_URI` and optionally `MONGODB_DB=drivewise`.
Set `SEED_MONGO=1` once to insert demo records into empty Mongo collections.

These endpoints exist on port 3001 (not port 8000):

```text
GET /api/dealerships
GET /api/dealerships/state/KS
GET /api/dealerships/1
GET /api/dealerships/1/reviews
```

## Grading evidence checklist

**Actual work is required, not random screenshots:**

- #1: Submit **this actual README file URL** (`/blob/main/README.md`).
- #2: Run Django server; capture the authentic `runserver` terminal output.
- #3/4: Submit GitHub links to `server/frontend/static/About.html` and `Contact.html`.
- #5/6, #8–11, #14–16: Use genuine responses from running services.
- #7: Submit URL to `server/frontend/src/components/Register/Register.jsx`.
- #12–13: Actually log in/out in `/admin/` and take screenshots.
- #17–22: Use running site to show filtering, sign-in, posting a review and the result.
- #23: Check that GitHub **Actions** is green and copy its real logs.
- #24–28: Require an actual deployed application; **not implemented here**.

README and source links alone do not guarantee points; the course grader decides.

## Run tests

```powershell
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check
cd server\frontend
npm install
npm run build
```

## Author

Alikhan Faizrakhman • Course: IBM Full-Stack Software Developer Capstone.
