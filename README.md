# Contact Management System

This is a simple Django application for managing contacts. It provides APIs for creating, reading, updating, and deleting contacts. Additionally, it supports searching contacts by name and phone number and exporting the contact list via email.

## API Endpoints

**List Contacts:** GET api/v1/directory/contacts/

**Create Contact:** POST api/v1/directory/contacts/

**Retrieve Contact:** GET api/v1/directory/contacts/<id>/

**Update Contact:** PUT api/v1/directory/contacts/<id>/ or PATCH api/v1/directory/contacts/<id>/

**Delete Contact:** DELETE api/v1/directory/contacts/<id>/

**Search Contacts:** GET api/v1/directory/search/?name=<name>&phone_number=<phone_number>

**Export Contacts:** GET api/v1/directory/export/

## Build the project by docker image

```dockerfile
version: '3.9'
services:
  dev-db:
    image: postgres:13
    ports:
      - 5434:5432
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: 1234
      POSTGRES_DB: Django

  web:
    image: zakilu/directory-web:latest
    command: sh -c "python3 manage.py migrate & celery -A directory worker -l info & gunicorn directory.wsgi:application --bind 0.0.0.0:8000"
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - dev-db
    restart: always

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
```

```bash
docker compose up -d
```

### example:

```bash
curl -X POST \
  http://35.72.177.254/api/v1/directory/ \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone_number": "1234567890"
}'
```

## Celery Configuration

```python
# Celery
BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Taipei'
# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
```

## Deployment (CI/CD) Workflow

1. Test
   Description: This job runs tests on the application code.
   Runs on: Ubuntu latest
   Steps:
   Checkout code
   Set up Python environment
   Set up Docker Buildx
   Install dependencies
   Build docker container for testing
   Run tests

2. Build and Upload Docker Image to Docker Hub
   Description: This job builds the Docker image for the application and uploads it to Docker Hub.
   Runs on: Ubuntu latest
   Needs: Test job
   Steps:
   Checkout repository
   Set up Docker Buildx
   Login to Docker Hub
   Build and push Docker image to Docker Hub

3. Deploy on EC2
   Description: This job deploys the application to an EC2 instance after merging changes into the develop branch.
   Runs on: Ubuntu latest
   Needs: Build and Upload Docker Image to Docker Hub job
   Steps:
   Deploy to EC2 using SSH
   Connects to the EC2 instance
   Pulls the latest Docker image from Docker Hub
   Starts the Docker containers on the EC2 instance
