# Leads Service

This service provides two webhook endpoints for logging lead information:

- `POST /residential-team` — Receives residential team leads
- `POST /commercial-team` — Receives commercial team leads

Each endpoint expects a JSON payload and logs the received data to the console.

## Running the Service

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8003
   ```

## Example Request

```
curl -X POST http://localhost:8003/residential-team \
     -H "Content-Type: application/json" \
     -d '{"name": "John Doe", "email": "john@example.com", "phone": "123-456-7890"}'
```
