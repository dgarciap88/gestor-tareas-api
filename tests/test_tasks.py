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


# ---------------------------------------------------------------------------
# Casos de error: crear tarea con título inválido
# ---------------------------------------------------------------------------

class TestCreateTaskErrors:
    def test_create_task_empty_title(self, client):
        resp = client.post("/tasks/", json={"title": ""})
        assert resp.status_code == 422
        assert resp.json()["detail"] == "El título debe tener al menos 3 caracteres"

    def test_create_task_short_title(self, client):
        resp = client.post("/tasks/", json={"title": "ab"})
        assert resp.status_code == 422
        assert resp.json()["detail"] == "El título debe tener al menos 3 caracteres"


# ---------------------------------------------------------------------------
# Casos de error: obtener tarea inexistente
# ---------------------------------------------------------------------------

class TestGetTaskErrors:
    def test_get_task_not_found(self, client):
        resp = client.get("/tasks/9999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Tarea no encontrada"


# ---------------------------------------------------------------------------
# Casos de error: actualizar tarea
# ---------------------------------------------------------------------------

class TestUpdateTaskErrors:
    def test_patch_task_already_done(self, client):
        # Creamos una tarea y la marcamos como done directamente en la BD
        create_resp = client.post(
            "/tasks/",
            json={"title": "tarea terminada", "status": "done"},
        )
        task_id = create_resp.json()["id"]
        resp = client.patch(
            f"/tasks/{task_id}", json={"title": "nuevo titulo"}
        )
        assert resp.status_code == 400
        assert resp.json()["detail"] == "Cannot update a task that is already done"

    def test_patch_task_not_found(self, client):
        resp = client.patch("/tasks/9999", json={"title": "nada"})
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Tarea no encontrada"


# ---------------------------------------------------------------------------
# Casos de error: eliminar tarea inexistente
# ---------------------------------------------------------------------------

class TestDeleteTaskErrors:
    def test_delete_task_not_found(self, client):
        resp = client.delete("/tasks/9999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Tarea no encontrada"