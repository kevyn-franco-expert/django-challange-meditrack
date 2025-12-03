# MediTrack API - Medical Management System

REST API for medical records management supporting 3 client types with different requirements.

## Quick Start with Docker

### Prerequisites
- Docker
- Docker Compose

### Run the Project

```bash
# 1. Clone repository
cd DjangoChallageTest

# 2. Build and start containers
docker-compose build
docker-compose up -d

# 3. Create and apply migrations
docker-compose exec web python manage.py makemigrations core patients records audit
docker-compose exec web python manage.py migrate

# 4. Access the API
# http://localhost:8000/api/
```

### Stop the Project

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (full cleanup)
docker-compose down -v
```

## Run Tests

```bash
# Run all tests
docker-compose exec web python manage.py test

# Run tests for specific app
docker-compose exec web python manage.py test apps.patients
docker-compose exec web python manage.py test apps.records
docker-compose exec web python manage.py test apps.audit

# View test coverage
docker-compose exec web python manage.py test --verbosity=2
```

## Authorization

The API uses header-based authorization to control access based on client type and user roles.

### Required Headers

All requests must include:
- `X-Client-ID`: Identifies the client making the request
- `X-User-Role`: (Optional) User role for hospitals (nurse/doctor)
- `X-Department`: (Optional) Department for clinics
- `X-Patient-Consent`: (Optional) Patient consent for mobile apps

### Examples

#### Legacy Hospital - Doctor Access
```bash
curl -X GET http://localhost:8000/api/patients/1/ \
  -H "X-Client-ID: legacy_hospital_1" \
  -H "X-User-Role: doctor"
```

#### Legacy Hospital - Nurse Access (Read-only)
```bash
curl -X GET http://localhost:8000/api/patients/1/ \
  -H "X-Client-ID: legacy_hospital_1" \
  -H "X-User-Role: nurse"
```

#### Modern Clinic - Department Based
```bash
curl -X GET http://localhost:8000/api/patients/1/ \
  -H "X-Client-ID: modern_clinic_1" \
  -H "X-Department: cardiology"
```

#### Mobile App - Patient Consent
```bash
curl -X GET http://localhost:8000/api/patients/1/ \
  -H "X-Client-ID: mobile_app_1" \
  -H "X-Patient-Consent: true"
```

## Postman

Import collection: `MediTrack_API_with_Auth.postman_collection.json`

The collection includes examples for all client types with appropriate headers.

## Useful Commands

```bash
# View logs
docker-compose logs -f web

# Access Django shell
docker-compose exec web python manage.py shell

# Access PostgreSQL
docker-compose exec db psql -U meditrack -d meditrack

# Create superuser
docker-compose exec web python manage.py createsuperuser

# SSN data migration
docker-compose exec web python manage.py migrate_ssn_data --dry-run
docker-compose exec web python manage.py migrate_ssn_data --batch-size=1000
```

## Main Endpoints

### Patients
- `GET /api/patients/` - List patients
- `POST /api/patients/` - Create patient
- `GET /api/patients/{id}/` - View patient
- `PATCH /api/patients/{id}/` - Update patient

### Medical Records
- `GET /api/records/` - List records
- `POST /api/records/` - Create record
- `GET /api/records/{id}/` - View record

### Client Types
- **Legacy Hospitals:** Required fields, rigid structure, role-based access (nurse/doctor)
- **Modern Clinics:** Optional fields, flexible schemas, department-based permissions
- **Mobile Apps:** Field selection, optimized responses, patient consent-based access

## Troubleshooting

### Error: "relation does not exist"
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### Clean Docker
```bash
docker system prune -a --volumes --force
```

## License

This project is part of a technical exercise for MediTrack.
