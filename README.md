# Customer Accounts

[![CI Build](https://github.com/ShriK1912/customer-accounts/actions/workflows/ci-build.yaml/badge.svg)](https://github.com/ShriK1912/customer-accounts/actions/workflows/ci-build.yaml)

Customer Accounts is a Flask microservice for creating, listing, reading,
updating, and deleting customer account records through a REST API.

## Project goals

- Manage customer accounts through a RESTful API.
- Run automated lint and unit-test checks with GitHub Actions.
- Add security headers and cross-origin resource sharing (CORS).
- Package the service in Docker and describe its Kubernetes deployment.

## Run locally

Install the dependencies and start the service:

```powershell
python -m pip install -r requirements.txt
python wsgi.py
```

The service listens on port 8080. API requests use the `/accounts` endpoint.
