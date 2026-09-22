# FindMeApartment (FMA) 🏢 Rent & Vacation Platform Backend

FMA is a production-ready, fully containerized vacation rental backend platform (an Airbnb clone) engineered using **Django 6.1**, **Django REST Framework (DRF)**, and **MySQL 8**. The system is optimized via reverse proxy routing using **Nginx**, automated process management with **Gunicorn**, and a standardized exception flow layer.

---

## 🛠️ Tech Stack & Core Infrastructure
* **Backend Framework:** Django 6.1.1 & Django REST Framework 3.18.1
* **Database engine:** MySQL 8.0 (with production health check monitoring)
* **WSGI HTTP Server:** Gunicorn 26.2.0
* **Reverse Proxy & Static Router:** Nginx (Latest Docker Image)
* **Authentication:** SimpleJWT (Automated claims updates & token rotating)
* **API Documentation:** OpenAPI Schema via `drf-spectacular` & Swagger UI
* **Global Error handling:** `drf-standardized-errors` custom conversion extensions

---

## 💎 Advanced Enterprise Architecture Features

### 1. Robust Soft Delete Mechanisms
* Customized database layer overrides (`UserSoftDeleteManager`, `BookingsSoftDeleteManager`, and `ListingsSoftDeleteManager`) mask archived elements from consumer-facing indexes (`deleted_at__isnull=True`).
* Administrative operations utilize hidden `.all_objects` model managers to preserve access to archived audit records, history tracking, and financial compliance metrics.

### 2. Multi-Role RBAC Security Matrix
* Automatically assigns a default `Tenant` security group upon successful account registration.
* Implements dynamic object-level permissions (`IsLandLord`, `IsReviewAuthorOrAdmin`) ensuring strict boundary parameters: tenants manage their own trips, hosts control their metadata, and public clients see strictly valid assets.

### 3. Financial & Transactional Integrity Guardrails
* **Immutable Snapshot Logging:** Finalized reservations trigger automated snapshot compilations (`snapshot_data`) locking property, host, and client metadata state records, isolating transaction history logs from later profile mutations.
* **Double-Booking Protection:** Model validations run active overlaps screening across `PENDING` and `CONFIRMED` states to enforce atomic date logic.
* **Operational Limits:** Incorporates age restrictions (18-120 years old), stays cap up to 30 nights, strict image validation upload policies (< 2 MB and verified extensions), and a 2-day minimum lock policy for booking cancellations.

### 4. Advanced Analytics & Optimized Queries
* Consolidates complex metrics over high volumes using centralized database aggregations (`Sum`, `Count`, `Q` filtering) calculated inside single atomic SQL execution tasks.
* Eradicates the `N+1` query degradation problem across deep object tables using eager entity loading filters (`select_related`, `prefetch_related`).

---

## 🚀 Orchestration & Rapid Deployment Guide

### 📋 Prerequisites
Ensure that you have **Docker** and **Docker Compose** installed on your hosting node.

### ⚡ Automatic Setup & Database Initialization
To clear old databases, perform fresh schema builds, configure system user roles, and fire up Nginx routing, run our custom bash orchestrator in your terminal window:
```bash
chmod +x first_init_n_reset_db.sh
./first_init_n_reset_db.sh
```

### 🐋 Operational Commands
* **Start infrastructure in background mode:**
  ```bash
  docker compose up -d
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
The backend features an isolated testing strategy with optimized environment adjustments. Running tests automatically overrides slow cryptographic mechanisms to use high-velocity MD5 algorithms, bringing execution speeds down to fractions of a second.

To execute the entire integration test suite, trigger the following task within the web layer:
```bash
docker compose exec web python manage.py test
```

---

## 🔗 Main API Navigation Index
* **Interactive Open API Specification:** `http://localhost/api/docs/` (Swagger UI Dashboard)
* **Static Reference Schema Catalog:** `http://localhost/api/redoc/`
* **Healthcheck Heartbeat Route:** `http://localhost/ping/`
