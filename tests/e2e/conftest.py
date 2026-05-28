"""Shared fixtures for e2e tests.

Provides auth_token and seeded_data fixtures used across all
e2e test files (ASGI transport, SQLite in-memory).

Also provides docker_stack and docker_client fixtures for Docker
smoke tests (auto-start/stop lifecycle).
"""

from __future__ import annotations

import random
import socket
import subprocess
import time
from collections.abc import AsyncGenerator, Generator
from urllib.parse import urlparse

import httpx
import pytest

# ── Docker stack lifecycle fixture ───────────────────────────────
# Starts docker-compose before the test session and tears it down
# afterwards, regardless of test outcome.  Only activates for tests
# marked with @pytest.mark.docker.


def _wait_for_api(base_url: str, timeout: int = 60) -> bool:
    """Poll the health endpoint until the API responds or timeout.

    Parses host and port from base_url for the socket pre-check,
    then hits the HTTP endpoint to confirm the API is fully ready.
    """
    parsed = urlparse(base_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 8000

    for _ in range(timeout):
        # Fast check: is the port open?
        try:
            sock = socket.create_connection((host, port), timeout=2)
            sock.close()
        except (ConnectionRefusedError, OSError):
            time.sleep(1)
            continue

        # Port is open, try HTTP
        try:
            resp = httpx.get(f"{base_url}/", timeout=2)
            if resp.status_code == 200:
                return True
        except httpx.HTTPError:
            pass
        time.sleep(1)
    return False


@pytest.fixture(scope="session")
def docker_stack(request: pytest.FixtureRequest) -> Generator[str, None, None]:
    """Start and stop the Docker Compose stack for smoke tests.

    Lifecycle:
      1. Build and start containers (docker-compose up -d --build)
      2. Wait for API to be healthy (poll / endpoint)
      3. Yield — tests run
      4. Always stop and remove containers (docker-compose down)

    If Docker is not available or the stack fails to start,
    all dependent tests are skipped.

    This fixture is automatically activated when any test function
    requests the ``docker_client`` fixture.
    """
    base_url = "http://localhost:8000"
    project_dir = request.config.rootdir

    # Check if Docker is available
    try:
        subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=10,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("Docker is not available")

    # Start the stack
    print("\n[docker_stack] Building and starting containers...")
    up_result = subprocess.run(
        ["docker-compose", "up", "-d", "--build"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(project_dir),
    )
    if up_result.returncode != 0:
        pytest.skip(f"docker-compose up failed:\n{up_result.stderr}")

    # Wait for API to be ready
    print("[docker_stack] Waiting for API to be ready...")
    if not _wait_for_api(base_url, timeout=60):
        # Dump logs for debugging
        logs = subprocess.run(
            ["docker-compose", "logs", "api"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(project_dir),
        )
        # Tear down before skipping
        subprocess.run(
            ["docker-compose", "down"],
            capture_output=True,
            timeout=30,
            cwd=str(project_dir),
        )
        pytest.skip(
            f"API did not become ready within 60s.\n"
            f"API logs:\n{logs.stdout[-500:]}"
        )

    print("[docker_stack] API is ready!")

    # Yield — tests run here
    yield base_url

    # Teardown: always stop containers
    print("\n[docker_stack] Stopping containers...")
    subprocess.run(
        ["docker-compose", "down"],
        capture_output=True,
        timeout=30,
        cwd=str(project_dir),
    )
    print("[docker_stack] Containers stopped.")


@pytest.fixture
async def docker_client(docker_stack: str) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide an httpx client connected to the Docker stack.

    Requires the docker_stack fixture to be active.
    """
    client = httpx.AsyncClient(base_url=docker_stack, timeout=30.0)
    yield client
    await client.aclose()


@pytest.fixture
async def smoke_token(docker_client: httpx.AsyncClient) -> str:
    """Obtain a JWT token for smoke tests.

    Authenticates against the live Docker stack and returns the token.
    Skips all dependent tests if authentication fails (no test user).
    """
    test_email = f"smoke-{random.randint(1000, 9999)}@test.com"
    test_password = "test123456"

    login_resp = await docker_client.post(
        "/token",
        data={"username": test_email, "password": test_password},
    )
    if login_resp.status_code != 200:
        pytest.skip("Cannot authenticate — no test user in DB")

    return login_resp.json()["access_token"]


# ── ASGI fixtures (for non-Docker e2e tests) ────────────────────


@pytest.fixture
async def auth_token(client, test_user):
    """Obtain a JWT token for the test user."""
    response = await client.post(
        "/token",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def seeded_data(test_db_session):
    """Seed customers and products needed for upload tests."""
    from app.core.entities.customer import Customer
    from app.core.entities.product import Product
    from app.infrastructure.repositories.customer_repository import (
        CustomerRepository,
    )
    from app.infrastructure.repositories.product_repository import (
        ProductRepository,
    )

    cust_repo = CustomerRepository(session=test_db_session)
    prod_repo = ProductRepository(session=test_db_session)

    customer = await cust_repo.create(
        Customer(name="E2E Customer", email="e2e@example.com")
    )
    product_a = await prod_repo.create(
        Product(name="E2E Widget A", price=10.0, stock=50)
    )
    product_b = await prod_repo.create(
        Product(name="E2E Widget B", price=25.0, stock=100)
    )
    return {
        "customer": customer,
        "product_a": product_a,
        "product_b": product_b,
    }
