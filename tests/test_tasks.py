"""Tests para la API de gestion de tareas."""

import pytest
from fastapi.testclient import TestClient
from aplicacion.principal import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Happy path: crear tarea
# ---------------------------------------------------------------------------

class TestCreateTaskHappyPath:
    def test_create_task_minimal(self, client):
        resp = client.post("/tasks/", json={"title": "mi tarea"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "mi tarea"
        assert body["description"] is None
        assert body["status"] == "pending"
        assert "id" in body
        assert "created_at" in body

    def test_create_task_with_all_fields(self, client):
        resp = client.post(
            "/tasks/",
            json={
                "title": "tarea completa",
                "description": "desc",
                "status": "in_progress",
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "tarea completa"
        assert body["description"] == "desc"
        assert body["status"] == "in_progress"


# ---------------------------------------------------------------------------
# Happy path: listar tareas
# ---------------------------------------------------------------------------

class TestListTasks:
    def test_list_tasks_empty(self, client):
        resp = client.get("/tasks/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_tasks_returns_created(self, client):
        client.post("/tasks/", json={"title": "tarea uno"})
        client.post("/tasks/", json={"title": "tarea dos"})
        resp = client.get("/tasks/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2