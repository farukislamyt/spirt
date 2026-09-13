# SPIRT API

The optional FastAPI layer exposes the same public-profile collection and reporting primitives as the Python package.

Install the API extra:

```bash
pip install 'spirt[api]'
```

Run locally:

```bash
uvicorn spirt.api:create_app --factory --host 127.0.0.1 --port 8000
```

## Endpoints

### `GET /health`

Returns service status and the installed SPIRT version.

### `GET /v1/providers`

Lists registered providers and their declared hosts.

### `GET /v1/profile?url=...`

Collects a single supported public profile URL and returns the structured `CollectionResult`.

### `POST /v1/report?format=json|markdown|html`

Accepts a JSON array of 1–100 public profile URLs and returns the rendered research report.

## API boundary

The API does not expand SPIRT's collection scope. The same public-data and network-safety boundaries apply to every endpoint.
