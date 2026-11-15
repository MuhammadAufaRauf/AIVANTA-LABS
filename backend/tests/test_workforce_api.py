def test_seed_departments_and_employees(client):
    departments = client.get("/api/v1/departments").json()
    employees = client.get("/api/v1/employees").json()
    assert len(departments) == 8
    assert {item["name"] for item in employees} == {"AI Manager", "AI Researcher", "AI Developer", "AI Secretary"}


def test_department_crud_and_protect_employees(client):
    response = client.post("/api/v1/departments", json={"name": "Legal", "description": ""})
    assert response.status_code == 201
    department_id = response.json()["id"]
    assert client.patch(f"/api/v1/departments/{department_id}", json={"description": "Legal support"}).status_code == 200
    employee_department = next(item for item in client.get("/api/v1/departments").json() if item["name"] == "Technology")
    assert client.delete(f"/api/v1/departments/{employee_department['id']}").status_code == 409
    assert client.delete(f"/api/v1/departments/{department_id}").status_code == 204
    assert client.delete(f"/api/v1/departments/{department_id}").status_code == 404
    assert client.post("/api/v1/departments", json={"name": "Management", "description": "duplicate"}).status_code == 409
    assert client.post("/api/v1/departments", json={"name": "", "description": ""}).status_code == 422


def test_employee_crud_validation_and_references(client):
    departments = {item["name"]: item["id"] for item in client.get("/api/v1/departments").json()}
    response = client.post("/api/v1/employees", json={
        "name": "Test Engineer", "position": "Engineer", "department_id": departments["Technology"],
        "description": "Test", "system_instructions": "", "ai_provider": "ollama", "ai_model": "local-model", "status": "active"
    })
    assert response.status_code == 201
    employee_id = response.json()["id"]
    assert client.get(f"/api/v1/employees/{employee_id}").json()["department_name"] == "Technology"
    assert client.patch(f"/api/v1/employees/{employee_id}", json={"status": "inactive"}).json()["status"] == "inactive"
    assert client.get("/api/v1/employees?status=inactive").status_code == 200
    assert client.patch(f"/api/v1/employees/{employee_id}", json={"department_id": 9999}).status_code == 404
    assert client.delete(f"/api/v1/employees/{employee_id}").status_code == 204


def test_task_crud_filters_and_employee_deletion_guard(client):
    employee = next(item for item in client.get("/api/v1/employees").json() if item["name"] == "AI Developer")
    response = client.post("/api/v1/tasks", json={
        "title": "Build API", "description": "Create endpoints", "assigned_employee_id": employee["id"],
        "priority": "high", "status": "todo", "due_date": None
    })
    assert response.status_code == 201
    task_id = response.json()["id"]
    assert response.json()["assigned_employee_name"] == "AI Developer"
    assert client.get("/api/v1/tasks?status=todo&priority=high&employee_id=" + str(employee["id"]) + "&search=API").json()[0]["id"] == task_id
    assert client.patch(f"/api/v1/tasks/{task_id}", json={"status": "completed"}).json()["status"] == "completed"
    assert client.delete(f"/api/v1/employees/{employee['id']}").status_code == 409
    assert client.delete(f"/api/v1/tasks/{task_id}").status_code == 204
    assert client.delete(f"/api/v1/tasks/{task_id}").status_code == 404


def test_project_relationship_progress_and_delete_validation(client):
    employee = client.get("/api/v1/employees").json()[0]
    response = client.post("/api/v1/projects", json={"name": "Launch", "description": "", "employee_ids": [employee["id"]], "status": "active", "priority": "medium"})
    assert response.status_code == 201
    project_id = response.json()["id"]
    assert response.json()["progress_percent"] == 0
    task = client.post("/api/v1/tasks", json={"title": "First", "project_id": project_id, "status": "completed"})
    assert task.status_code == 201
    detail = client.get(f"/api/v1/projects/{project_id}").json()
    assert detail["task_count"] == 1 and detail["completed_task_count"] == 1 and detail["progress_percent"] == 100
    assert client.delete(f"/api/v1/projects/{project_id}").status_code == 409
    assert client.patch(f"/api/v1/projects/{project_id}", json={"employee_ids": []}).status_code == 200
    assert client.delete(f"/api/v1/tasks/{task.json()['id']}").status_code == 204
    assert client.get("/api/v1/projects?status=active&priority=medium&search=Launch").json()[0]["id"] == project_id
    assert client.patch(f"/api/v1/projects/{project_id}", json={"deadline": "2020-01-01", "start_date": "2021-01-01"}).status_code == 422
    assert client.delete(f"/api/v1/projects/{project_id}").status_code == 204
    assert client.delete(f"/api/v1/projects/{project_id}").status_code == 404


def test_dashboard_stats_are_database_backed(client):
    stats = client.get("/api/v1/dashboard/stats").json()
    assert stats == {"total_employees": 4, "active_employees": 4, "total_departments": 8, "total_tasks": 0, "completed_tasks": 0, "ongoing_projects": 0}
