from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.db.models import (
    Department,
    Employee,
    EmployeeStatus,
    Project,
    ProjectStatus,
    Task,
    TaskStatus,
)

INITIAL_DEPARTMENTS = (
    ("Management", "Company leadership and operations"),
    ("Technology", "Software engineering and quality assurance"),
    ("Research", "Research and data analysis"),
    ("Marketing", "Marketing and search optimization"),
    ("Creative", "Design and content production"),
    ("Finance", "Financial planning and accounting"),
    ("Administration", "Administration and people operations"),
    ("Customer Support", "Customer care and support"),
)

INITIAL_EMPLOYEES = (
    ("AI Manager", "AI Manager", "Management", "Coordinates company work and reports to the CEO."),
    ("AI Researcher", "AI Researcher", "Research", "Supports research and evidence gathering."),
    ("AI Developer", "AI Developer", "Technology", "Supports software development tasks."),
    ("AI Secretary", "AI Secretary", "Administration", "Supports administrative work and organization."),
)


def seed_workforce(db: Session) -> None:
    for name, description in INITIAL_DEPARTMENTS:
        if db.scalar(select(Department).where(Department.name == name)) is None:
            db.add(Department(name=name, description=description))
    db.flush()
    departments = {department.name: department.id for department in db.scalars(select(Department)).all()}
    for name, position, department_name, description in INITIAL_EMPLOYEES:
        existing = db.scalar(select(Employee).where(Employee.name == name, Employee.department_id == departments[department_name]))
        if existing is None:
            db.add(Employee(name=name, position=position, department_id=departments[department_name], description=description))
    db.commit()


def department_read(department: Department) -> dict:
    return {
        "id": department.id,
        "name": department.name,
        "description": department.description,
        "created_at": department.created_at,
        "updated_at": department.updated_at,
        "employee_count": len(department.employees),
    }


def employee_read(employee: Employee) -> dict:
    return {
        "id": employee.id,
        "name": employee.name,
        "position": employee.position,
        "department_id": employee.department_id,
        "department_name": employee.department.name,
        "description": employee.description,
        "system_instructions": employee.system_instructions,
        "ai_provider": employee.ai_provider,
        "ai_model": employee.ai_model,
        "status": employee.status,
        "created_at": employee.created_at,
        "updated_at": employee.updated_at,
    }


def task_read(task: Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "assigned_employee_id": task.assigned_employee_id,
        "assigned_employee_name": task.assigned_employee.name if task.assigned_employee else None,
        "project_id": task.project_id,
        "project_name": task.project.name if task.project else None,
        "priority": task.priority,
        "status": task.status,
        "due_date": task.due_date,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


def project_read(project: Project) -> dict:
    task_count = len(project.tasks)
    completed = sum(task.status == TaskStatus.completed for task in project.tasks)
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "start_date": project.start_date,
        "deadline": project.deadline,
        "status": project.status,
        "priority": project.priority,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "employee_ids": [employee.id for employee in project.employees],
        "employee_names": [employee.name for employee in project.employees],
        "task_count": task_count,
        "completed_task_count": completed,
        "progress_percent": round(completed * 100 / task_count) if task_count else 0,
    }


def get_department_or_404(db: Session, department_id: int) -> Department:
    from fastapi import HTTPException

    department = db.get(Department, department_id)
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


def get_employee_or_404(db: Session, employee_id: int) -> Employee:
    from fastapi import HTTPException

    employee = db.scalar(select(Employee).options(selectinload(Employee.department)).where(Employee.id == employee_id))
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


def get_task_or_404(db: Session, task_id: int) -> Task:
    from fastapi import HTTPException

    task = db.scalar(select(Task).options(selectinload(Task.assigned_employee), selectinload(Task.project)).where(Task.id == task_id))
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def get_project_or_404(db: Session, project_id: int) -> Project:
    from fastapi import HTTPException

    project = db.scalar(
        select(Project)
        .options(selectinload(Project.employees), selectinload(Project.tasks))
        .where(Project.id == project_id)
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def validate_employee_department(db: Session, department_id: int) -> None:
    get_department_or_404(db, department_id)


def validate_task_references(db: Session, assigned_employee_id: int | None, project_id: int | None) -> None:
    from fastapi import HTTPException

    if assigned_employee_id is not None and db.get(Employee, assigned_employee_id) is None:
        raise HTTPException(status_code=404, detail="Assigned employee not found")
    if project_id is not None and db.get(Project, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")


def validate_project_employees(db: Session, employee_ids: list[int]) -> list[Employee]:
    from fastapi import HTTPException

    employees = list(db.scalars(select(Employee).where(Employee.id.in_(employee_ids))).all()) if employee_ids else []
    if len(employees) != len(employee_ids):
        raise HTTPException(status_code=404, detail="One or more assigned employees were not found")
    return employees


def commit_or_conflict(db: Session, message: str = "A resource with these details already exists") -> None:
    from fastapi import HTTPException

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail=message) from error


def dashboard_stats(db: Session) -> dict[str, int]:
    return {
        "total_employees": db.scalar(select(func.count(Employee.id))) or 0,
        "active_employees": db.scalar(select(func.count(Employee.id)).where(Employee.status == EmployeeStatus.active)) or 0,
        "total_departments": db.scalar(select(func.count(Department.id))) or 0,
        "total_tasks": db.scalar(select(func.count(Task.id))) or 0,
        "completed_tasks": db.scalar(select(func.count(Task.id)).where(Task.status == TaskStatus.completed)) or 0,
        "ongoing_projects": db.scalar(select(func.count(Project.id)).where(Project.status == ProjectStatus.active)) or 0,
    }
