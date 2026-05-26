"""Tests para la API de gestión de tareas.

Prioriza casos de error y casos límite sobre el happy path.
"""

import pytest

from fastapi.testclient import TestClient

from aplicacion.principal import app


# ---------------------------------------------------------------------------
# Fixture del cliente de test (usado por todos los tests de endpoint)
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# GET /tasks/{task_id} — errores y límites
# ---------------------------------------------------------------------------


class TestGetTaskErrors:
    def test_get_nonexistent_task_returns_404(self, client):
        resp = client.get("/tasks/9999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Task not found"

    def test_get_task_id_zero_returns_404(self, client):
        resp = client.get("/tasks/0")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Task not found"

    def test_get_task_negative_id_returns_404(self, client):
        resp = client.get("/tasks/-1")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Task not found"

    def test_get_task_string_id_returns_422(self, client):
        resp = client.get("/tasks/abc")
        assert resp.status_code == 422
        assert "detail" in resp.json()

    def test_get_task_float_id_returns_422(self, client):
        resp = client.get("/tasks/1.5")
        assert resp.status_code == 422
        assert "detail" in resp.json()


# ---------------------------------------------------------------------------
# POST /tasks/ — errores y validación
# ---------------------------------------------------------------------------


class TestCreateTaskErrors:
    def test_create_task_missing_title_returns_422(self, client):
        resp = client.post("/tasks/", json={})
        assert resp.status_code == 422
        assert "detail" in resp.json()

    def test_create_task_null_title_returns_422(self, client):
        resp = client.post("/tasks/", json={"title": None})
        assert resp.status_code == 422
        assert "detail" in resp.json()

    def test_create_task_invalid_status_returns_422(self, client):
        resp = client.post(
            "/tasks/",
            json={"title": "t", "status": "invalid_status"},
        )
        assert resp.status_code == 422
        assert "detail" in resp.json()

    def test_create_task_extra_fields_are_ignored(self, client):
        resp = client.post(
            "/tasks/",
            json={"title": "t", "extra_field": "ignored"},
        )
        assert resp.status_code == 201
        assert "extra_field" not in resp.json()

    def test_create_task_empty_body_returns_422(self, client):
        resp = client.post(
            "/tasks/",
            content=b"",
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 422
        assert "detail" in resp.json()

    def test_create_task_non_json_body_returns_422(self, client):
        resp = client.post(
            "/tasks/",
            content=b"not json",
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 422
        assert "detail" in resp.json()

    def test_create_task_title_only_whitespace(self, client):
        resp = client.post("/tasks/", json={"title": "   "})
        assert resp.status_code == 201

    def test_create_task_very_long_title(self, client):
        long_title = "x" * 1000
        resp = client.post("/tasks/", json={"title": long_title})
        assert resp.status_code == 201
        assert resp.json()["title"] == long_title

    def test_create_task_title_integer_returns_422(self, client):
        resp = client.post("/tasks/", json={"title": 12345})
        assert resp.status_code == 422
        assert "detail" in resp.json()


# ---------------------------------------------------------------------------
# PATCH /tasks/{task_id} — errores y límites
# ---------------------------------------------------------------------------


class TestUpdateTaskErrors:
    def test_update_nonexistent_task_returns_404(self, client):
        resp = client.patch("/tasks/9999", json={"title": "new"})
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Task not found"

    def test_update_task_invalid_status_returns_422(self, client):
        create = client.post("/tasks/", json={"title": "t"})
        tid = create.json()["id"]
        resp = client.patch(
            f"/tasks/{tid}", json={"status": "bad"}
        )
        assert resp.status_code == 422
        assert "detail" in resp.json()

    def test_update_task_empty_body_no_changes(self, client):
        create = client.post(
            "/tasks/", json={"title": "original"}
        )
        tid = create.json()["id"]
        resp = client.patch(f"/tasks/{tid}", json={})
        assert resp.status_code == 200
        assert resp.json()["title"] == "original"

    def test_update_task_string_id_returns_422(self, client):
        resp = client.patch("/tasks/abc", json={"title": "x"})
        assert resp.status_code == 422
        assert "detail" in resp.json()

    def test_update_task_null_title_triggers_db_error(self, client):
        from sqlalchemy.exc import IntegrityError

        create = client.post("/tasks/", json={"title": "t"})
        tid = create.json()["id"]
        with pytest.raises(IntegrityError):
            client.patch(f"/tasks/{tid}", json={"title": None})

    def test_update_task_null_description(self, client):
        create = client.post(
            "/tasks/",
            json={"title": "t", "description": "desc"},
        )
        tid = create.json()["id"]
        resp = client.patch(
            f"/tasks/{tid}", json={"description": None}
        )
        assert resp.status_code == 200
        assert resp.json()["description"] is None


# ---------------------------------------------------------------------------
# DELETE /tasks/{task_id} — errores y límites
# ---------------------------------------------------------------------------


class TestDeleteTaskErrors:
    def test_delete_nonexistent_task_returns_404(self, client):
        resp = client.delete("/tasks/9999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Task not found"

    def test_delete_task_string_id_returns_422(self, client):
        resp = client.delete("/tasks/abc")
        assert resp.status_code == 422
        assert "detail" in resp.json()

    def test_delete_task_twice_returns_404_second_time(self, client):
        create = client.post(
            "/tasks/", json={"title": "to_delete"}
        )
        tid = create.json()["id"]
        first = client.delete(f"/tasks/{tid}")
        assert first.status_code == 204
        second = client.delete(f"/tasks/{tid}")
        assert second.status_code == 404
        assert second.json()["detail"] == "Task not found"


# ---------------------------------------------------------------------------
# GET /tasks/ — lista vacía y límites
# ---------------------------------------------------------------------------


class TestListTasks:
    def test_list_tasks_empty(self, client):
        resp = client.get("/tasks/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_tasks_returns_all_created(self, client):
        for i in range(5):
            client.post("/tasks/", json={"title": f"task_{i}"})
        resp = client.get("/tasks/")
        assert resp.status_code == 200
        assert len(resp.json()) == 5


# ---------------------------------------------------------------------------
# POST /tasks/ — happy path y campos opcionales
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

    def test_create_task_status_done(self, client):
        resp = client.post(
            "/tasks/",
            json={"title": "done task", "status": "done"},
        )
        assert resp.status_code == 201
        assert resp.json()["status"] == "done"

    def test_create_task_empty_description(self, client):
        resp = client.post(
            "/tasks/", json={"title": "t", "description": ""}
        )
        assert resp.status_code == 201
        assert resp.json()["description"] == ""


# ---------------------------------------------------------------------------
# GET /tasks/{task_id} — happy path
# ---------------------------------------------------------------------------


class TestGetTaskHappyPath:
    def test_get_created_task(self, client):
        create = client.post(
            "/tasks/", json={"title": "read me"}
        )
        tid = create.json()["id"]
        resp = client.get(f"/tasks/{tid}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "read me"
        assert resp.json()["id"] == tid


# ---------------------------------------------------------------------------
# PATCH /tasks/{task_id} — happy path
# ---------------------------------------------------------------------------


class TestUpdateTaskHappyPath:
    def test_update_title_only(self, client):
        create = client.post("/tasks/", json={"title": "old"})
        tid = create.json()["id"]
        resp = client.patch(
            f"/tasks/{tid}", json={"title": "new"}
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "new"

    def test_update_status(self, client):
        create = client.post("/tasks/", json={"title": "t"})
        tid = create.json()["id"]
        resp = client.patch(
            f"/tasks/{tid}", json={"status": "done"}
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "done"

    def test_update_multiple_fields(self, client):
        create = client.post("/tasks/", json={"title": "t"})
        tid = create.json()["id"]
        resp = client.patch(
            f"/tasks/{tid}",
            json={
                "title": "updated",
                "description": "new desc",
                "status": "in_progress",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["title"] == "updated"
        assert body["description"] == "new desc"
        assert body["status"] == "in_progress"


# ---------------------------------------------------------------------------
# DELETE /tasks/{task_id} — happy path
# ---------------------------------------------------------------------------


class TestDeleteTaskHappyPath:
    def test_delete_task_returns_204(self, client):
        create = client.post(
            "/tasks/", json={"title": "delete me"}
        )
        tid = create.json()["id"]
        resp = client.delete(f"/tasks/{tid}")
        assert resp.status_code == 204
        assert resp.content == b""

    def test_deleted_task_not_in_list(self, client):
        create = client.post("/tasks/", json={"title": "gone"})
        tid = create.json()["id"]
        client.delete(f"/tasks/{tid}")
        resp = client.get("/tasks/")
        ids = [t["id"] for t in resp.json()]
        assert tid not in ids


# ---------------------------------------------------------------------------
# Modelo y esquemas — cobertura directa
# ---------------------------------------------------------------------------


class TestTaskStatusEnum:
    def test_all_status_values(self):
        from aplicacion.modelos import TaskStatus

        assert TaskStatus.pending.value == "pending"
        assert TaskStatus.in_progress.value == "in_progress"
        assert TaskStatus.done.value == "done"
        assert len(TaskStatus) == 3

    def test_status_is_str(self):
        from aplicacion.modelos import TaskStatus

        assert isinstance(TaskStatus.pending, str)


class TestSchemas:
    def test_task_create_defaults(self):
        from aplicacion.esquemas import TaskCreate

        t = TaskCreate(title="test")
        assert t.description is None
        assert t.status.value == "pending"

    def test_task_update_all_none(self):
        from aplicacion.esquemas import TaskUpdate

        t = TaskUpdate()
        assert t.title is None
        assert t.description is None
        assert t.status is None

    def test_task_response_from_attributes(self):
        from aplicacion.esquemas import TaskResponse

        assert TaskResponse.model_config["from_attributes"] is True


# ---------------------------------------------------------------------------
# base_de_datos — generador get_db
# ---------------------------------------------------------------------------


class TestGetDb:
    def test_get_db_yields_and_closes(self):
        from aplicacion.base_de_datos import get_db

        gen = get_db()
        session = next(gen)
        assert session is not None
        try:
            gen.send(None)
        except StopIteration:
            pass

    def test_get_db_closes_on_exception(self):
        from aplicacion.base_de_datos import get_db

        gen = get_db()
        next(gen)
        try:
            gen.throw(RuntimeError("test error"))
        except RuntimeError:
            pass


# ---------------------------------------------------------------------------
# Flujo completo CRUD — integración
# ---------------------------------------------------------------------------


class TestCRUDFlow:
    def test_full_lifecycle(self, client):
        created = client.post(
            "/tasks/",
            json={
                "title": "lifecycle",
                "description": "d",
                "status": "pending",
            },
        )
        assert created.status_code == 201
        tid = created.json()["id"]

        fetched = client.get(f"/tasks/{tid}")
        assert fetched.status_code == 200
        assert fetched.json()["title"] == "lifecycle"

        updated = client.patch(
            f"/tasks/{tid}", json={"status": "in_progress"}
        )
        assert updated.status_code == 200
        assert updated.json()["status"] == "in_progress"

        deleted = client.delete(f"/tasks/{tid}")
        assert deleted.status_code == 204

        gone = client.get(f"/tasks/{tid}")
        assert gone.status_code == 404
        assert gone.json()["detail"] == "Task not found"
