# Dewey Decimal API

This API provides a simple way to look up Dewey Decimal subjects based on their codes.

## Endpoints

### GET /api/dewey

Returns the subject for a given Dewey Decimal code.

**Parameters:**

- `code` (string, required): The Dewey Decimal code to look up.

**Example Request:**

```bash
curl "http://127.0.0.1:5001/api/dewey?code=510"
```

**Example Response:**

```json
{
  "name": "Mathematics"
}
```

**Error Responses:**

- `400 Bad Request`: If the `code` parameter is not provided.
- `404 Not Found`: If the Dewey Decimal code is not found.

## How to Run

1.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the API:
    ```bash
    python api/dewey_decimal.py
    ```
The API will be available at `http://127.0.0.1:5001`.
