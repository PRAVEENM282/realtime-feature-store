# Testing Guide

This project uses a containerized testing strategy to ensure all dependencies (like `faust`, `kafka`, `postgres`) are available and consistent with the production environment.

## How to Run Tests

To run the full test suite, use the helper service defined in `docker-compose.yml`:

```bash
docker compose run --rm tests
```

This command will:
1. Build/start a temporary test container (based on the `faust_app` image).
2. Install test dependencies (`pytest`, `httpx`, `asyncpg`, etc.).
3. Run `pytest` against the mounted code in the `tests/`, `services/`, and root directories.
4. Clean up the container after execution.

## Test Structure

*   **`tests/integration/`**: End-to-end tests that verify the full pipeline (Producer -> Kafka -> Faust -> DB -> API).
    *   `test_e2e_pipeline.py`: Produces a Kafka event and polls the API until the processed feature appears.
*   **`tests/unit/`**: Isolated unit tests for specific logic.
    *   `test_faust_features.py`: Tests the windowing and counting logic in Faust agents.
    *   `test_api_validation.py`: Tests input validation for the FastAPI endpoints.

## Current Coverage & Strategy

Currently, the tests cover the **Critical Path**:
1.  **Connectivity**: Verifies services can talk to each other (Test runner <-> Kafka/API).
2.  **Core Logic**: Verifies the Faust windowing aggregation works correctly.
3.  **Data Flow**: Verifies an event sent to Kafka actually persists to the DB and is retrievable via API.

**Is this enough?**
*   **For Development/Debugging**: Yes, this confirms the system is functional and stable.
*   **For Production**: You should aim for higher coverage. reliable systems usually add:
    *   **Negative Test Cases**: What happens if the DB is down? What if the API gets invalid JSON?
    *   **Performance Tests**: Can it handle 1000 events/sec?
    *   **Edge Cases**: Empty windows, duplicate user IDs, clock skew, etc.
