
import pytest
from app import create_app


@pytest.fixture()
def client(tmp_path):
    database = tmp_path / "test.db"

    app = create_app({
        "TESTING": True,
        "DATABASE": str(database)
    })

    with app.test_client() as client:
        yield client


def test_create_task(client):
    response = client.post("/tasks", json={
        "title": "Estudar DevOps",
        "description": "Aprender Docker e CI/CD"
    })

    assert response.status_code == 201

    data = response.get_json()

    assert data["title"] == "Estudar DevOps"
    assert data["description"] == "Aprender Docker e CI/CD"
    assert data["completed"] is False


def test_list_tasks(client):
    client.post("/tasks", json={
        "title": "Estudar Python"
    })

    response = client.get("/tasks")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["title"] == "Estudar Python"


def test_get_task(client):
    create_response = client.post("/tasks", json={
        "title": "Minha tarefa"
    })

    task_id = create_response.get_json()["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.get_json()["title"] == "Minha tarefa"


def test_update_task(client):
    create_response = client.post("/tasks", json={
        "title": "Tarefa antiga"
    })

    task_id = create_response.get_json()["id"]

    response = client.put(f"/tasks/{task_id}", json={
        "title": "Tarefa atualizada",
        "description": "Nova descrição",
        "completed": True
    })

    assert response.status_code == 200

    data = response.get_json()

    assert data["title"] == "Tarefa atualizada"
    assert data["description"] == "Nova descrição"
    assert data["completed"] is True


def test_delete_task(client):
    create_response = client.post("/tasks", json={
        "title": "Tarefa para excluir"
    })

    task_id = create_response.get_json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 200

    get_response = client.get(f"/tasks/{task_id}")

    assert get_response.status_code == 404


def test_task_not_found(client):
    response = client.get("/tasks/999")

    assert response.status_code == 404


def test_create_task_without_title(client):
    response = client.post("/tasks", json={
        "description": "Tarefa sem título"
    })

    assert response.status_code == 400


def test_create_task_with_invalid_json(client):
    response = client.post(
        "/tasks",
        data="conteudo inválido",
        content_type="application/json"
    )

    assert response.status_code == 400
