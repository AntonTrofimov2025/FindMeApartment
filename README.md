# FindMeApartment (FMA) 🏢 Rent & Vacation Platform Backend

FMA is a fully containerized vacation rental platform (an Airbnb / Booking.com–style clone) built with **Django 6.1**, **Django REST Framework**, and **MySQL 8.4**. Traffic is routed by **Nginx** — API and admin requests go to **Gunicorn**, everything else to a **React + TypeScript** single-page frontend — and every error leaves the API in one standardized JSON shape.

---

## 🛠️ Tech Stack & Core Infrastructure
* **Backend Framework:** Django 6.1.1 & Django REST Framework 3.18.1 (Python 3.13)
* **Database engine:** MySQL 8.4 (with container health check monitoring)
* **WSGI HTTP Server:** Gunicorn 26.2.0 (2 workers, automatic worker recycling via `--max-requests`)
* **Reverse Proxy & Static Router:** Nginx — serves `/static/` and `/media/`, proxies `^/(api|admin)/` to Gunicorn, forwards all other routes to the frontend container
* **Frontend:** React + TypeScript + Tailwind CSS, built in a multi-stage Docker image and served by `nginx:alpine`
* **Authentication:** SimpleJWT (5-minute access tokens, rotating refresh tokens with blacklisting)
* **Media Storage:** AWS S3 via `django-storages` in production, local filesystem in development and tests
* **API Documentation:** OpenAPI schema via `drf-spectacular` with Swagger UI and ReDoc
* **Global Error handling:** `drf-standardized-errors` with a custom handler that converts model-level `ValidationError`s into structured `400` responses
* **Audit Trail:** `django-simple-history` on bookings
* **Continuous Integration:** GitHub Actions runs the full test suite on every push and pull request

---

## 💎 Advanced Enterprise Architecture Features

### 1. Robust Soft Delete Mechanisms
* Custom default managers (`UserSoftDeleteManager`, `ListingsSoftDeleteManager`, `PhotoSoftDeleteManager`, `BookingsSoftDeleteManager`, `ReviewsSoftDeleteManager`) hide archived records from every consumer-facing query (`deleted_at__isnull=True`), and their querysets turn bulk `.delete()` into a soft delete.
* Administrative operations use the `.all_objects` managers to keep archived records available for audits, history tracking, and financial reporting.
* Uniqueness rules (a landlord's addresses, photo numbering) are enforced in `clean()` against **active** records only, under row-level locks (`select_for_update`), so soft-deleted records never block re-creation.
* Deletion cascades are guarded: a listing or a landlord account with confirmed or in-progress bookings cannot be deleted, and a deleted landlord's listings are hidden from the catalog together with the account.
* A deleted review can be restored: leaving a review again for the same booking revives the archived record with the new content.

### 2. Multi-Role RBAC Security Matrix
* Every new account joins the `Tenant` group automatically; `POST /api/users/me/become-landlord/` moves it to `Landlord`. The role change is one-way, and landlords can no longer book stays.
* Group permissions are seeded from a single `ROLE_PERMISSION` map in settings (`manage.py create_groups`) and enforced through `DjangoModelPermissions` where model-level rights matter.
* Object-level permissions (`IsLandLord`, `IsLandLordOrReadOnly`, `IsReviewAuthorOrAdmin`) keep strict boundaries: tenants manage their own trips, hosts manage their own listings and guests' bookings, and anonymous visitors see only active listings.
* A host's exact address (street, house and apartment number) stays hidden — in listings and in booking snapshots — until that host confirms the guest's booking.
* Password changes require the current password, validate the new one against Django's password validators, and revoke every active session by blacklisting all outstanding refresh tokens. Profile updates can never change the password or email.

### 3. Financial & Transactional Integrity Guardrails
* **Immutable Snapshot Logging:** When a booking is created (or its dates change), a snapshot (`snapshot_data`) freezes the tenant's contact details, the property data, the stay details and the total price, so later profile or listing edits never rewrite financial history.
* **Double-Booking Protection:** Overlapping dates are rejected against every occupying status (`PENDING`, `CONFIRMED`, `CHECKED_IN`, `COMPLETED`), and the booking save runs inside a transaction that locks the target listing row.
* **Lifecycle State Machine:** `PENDING → CONFIRMED / REJECTED / CANCELLED`, `CONFIRMED → CHECKED_IN / CANCELLED`, and a scheduled job that completes finished stays and cancels requests the host never answered. Check-in is only possible between the arrival date and the departure date.
* **Operational Limits:** Age restrictions (18–120 years), stays of up to 30 nights, no bookings more than one year ahead, image uploads under 2 MB with verified formats (including HEIC/HEIF), and a 2-day minimum notice for cancelling a confirmed booking.
* **Transactional Email Notifications:** HTML emails for new requests, confirmations, rejections and cancellations (to both parties) are dispatched only after the database transaction commits, and the scheduled maintenance job never triggers them.

### 4. Advanced Analytics & Optimized Queries
* `GET /api/bookings/analytics/` gives landlords earnings, booking counters per status, and the properties that have received bookings — all from a single aggregated SQL query (`Sum`, `Count`, `Q` filters).
* Listing ratings and the "does this user have a confirmed booking here?" flag are computed as queryset annotations (`Avg`, `Exists` + `OuterRef`) instead of per-row queries, and related objects are loaded eagerly (`select_related`, `prefetch_related`) to avoid the `N+1` problem.
* Catalog filtering supports country, city (prefix match), district, property type, rooms, minimum guest capacity, and price ranges calculated on the **discounted** price.

---

## 🚀 Orchestration & Rapid Deployment Guide

### 📋 Prerequisites
Ensure that you have **Docker** and **Docker Compose** installed on your hosting node, plus a `.env` file in the project root (database credentials, `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and the `AWS_*` variables when `DEBUG=False`).

On a fresh **AWS EC2** instance (Amazon Linux), `FmaProjectEC2AWS.sh` installs Docker, Docker Compose, Buildx, Git and cron, sets the server time zone to Europe/Berlin, and clones the repository into `/fma`. Create `.env` there before running the setup script below.

### ⚡ Automatic Setup & Database Initialization
To apply migrations, collect static files, create the user roles, and schedule maintenance jobs, run the setup script from the project root:
```bash
chmod +x project_first_initialization.sh
./project_first_initialization.sh
```
The script registers two nightly cron jobs: `flushexpiredtokens` (clears expired JWT blacklist entries) and `close_expired_bookings` (completes finished stays and cancels expired requests).

### 🐋 Operational Commands
* **Start infrastructure in background mode:**
  ```bash
  docker compose up -d
  ```
* **Deploy new code (the application code is baked into the image):**
  ```bash
  git pull
  docker compose up -d --build
  docker compose exec web python manage.py migrate
  ```
* **Graceful shutdown and container clearance:**
  ```bash
  docker compose down
  ```
* **View container background logs:**
  ```bash
  docker compose logs -f web
  ```

---

## 🧪 Testing Suite Execution
The backend has an isolated testing strategy: in test mode, password hashing switches to fast MD5, media files go to a separate `test_media` directory that is removed after the run, and S3 is never used. This keeps the whole suite fast.

To execute the entire integration test suite, trigger the following task within the web layer:
```bash
docker compose exec web python manage.py test
```
The same suite runs automatically in **GitHub Actions** (`.github/workflows/ci.yml`) against a MySQL 8.4 service container on every push and pull request to `main`/`master`.

---

## 🔗 Main API Navigation Index
* **Interactive Open API Specification:** `http://localhost/api/docs/` (Swagger UI Dashboard)
* **Static Reference Schema Catalog:** `http://localhost/api/redoc/`
* **Raw OpenAPI Schema:** `http://localhost/api/schema/`
* **Django Administration:** `http://localhost/admin/`
* **Internal Docker Infrastructure Heartbeat:** Isolated at container level (`http://localhost:8000/ping/`). Monitored strictly via Docker Engine Healthcheck matrix; Nginx returns `404` for `/ping/` from outside.
