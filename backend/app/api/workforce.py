from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Department, Employee, EmployeeStatus, Project, ProjectEmployee, ProjectStatus, Task, TaskPriority, TaskStatus
from app.db.session import get_db
from app.schemas import (
    DashboardStats,
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate,
    EmployeeCreate,
    EmployeeRead,
    EmployeeUpdate,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from app.services.workforce import (
    commit_or_conflict,
    dashboard_stats,
    department_read,
    employee_read,
    get_department_or_404,
    get_employee_or_404,
    get_project_or_404,
    get_task_or_404,
    project_read,
    task_read,
    validate_employee_department,
    validate_project_employees,
    validate_task_references,
)

router = APIRouter()


@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    return dashboard_stats(db)


@router.get("/departments", response_model=list[DepartmentRead])
def list_departments(db: Session = Depends(get_db)):
    departments = db.scalars(select(Department).options(selectinload(Department.employees)).order_by(Department.name)).all()
    return [department_read(department) for department in departments]


@router.post("/departments", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    department = Department(**payload.model_dump())
    db.add(department)
    commit_or_conflict(db, "Department name already exists")
    db.refresh(department)
    return department_read(department)


@router.get("/departments/{department_id}", response_model=DepartmentRead)
def read_department(department_id: int, db: Session = Depends(get_db)):
    department = db.scalar(select(Department).options(selectinload(Department.employees)).where(Department.id == department_id))
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return department_read(department)


@router.get("/departments/{department_id}/employees", response_model=list[EmployeeRead])
def list_department_employees(department_id: int, db: Session = Depends(get_db)):
    get_department_or_404(db, department_id)
    employees = db.scalars(select(Employee).options(selectinload(Employee.department)).where(Employee.department_id == department_id).order_by(Employee.name)).all()
    return [employee_read(employee) for employee in employees]


@router.patch("/departments/{department_id}", response_model=DepartmentRead)
def update_department(department_id: int, payload: DepartmentUpdate, db: Session = Depends(get_db)):
    department = get_department_or_404(db, department_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(department, key, value)
    commit_or_conflict(db, "Department name already exists")
    db.refresh(department)
    return department_read(department)


@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(department_id: int, db: Session = Depends(get_db)):
    department = get_department_or_404(db, department_id)
    if department.employees:
        raise HTTPException(status_code=409, detail="Cannot delete a department while it has employees")
    db.delete(department)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/employees", response_model=list[EmployeeRead])
def list_employees(
    department_id: int | None = None,
    status_filter: EmployeeStatus | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None, max_length=120),
    db: Session = Depends(get_db),
):
    query = select(Employee).options(selectinload(Employee.department)).order_by(Employee.name)
    if department_id is not None:
        query = query.where(Employee.department_id == department_id)
    if status_filter is not None:
        query = query.where(Employee.status == status_filter)
    if search:
        query = query.where(Employee.name.ilike(f"%{search.strip()}%"))
    return [employee_read(employee) for employee in db.scalars(query).all()]


@router.post("/employees", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    validate_employee_department(db, payload.department_id)
    employee = Employee(**payload.model_dump())
    db.add(employee)
    commit_or_conflict(db, "Employee with this name already exists in the department")
    return employee_read(get_employee_or_404(db, employee.id))


@router.get("/employees/{employee_id}", response_model=EmployeeRead)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    return employee_read(get_employee_or_404(db, employee_id))


@router.patch("/employees/{employee_id}", response_model=EmployeeRead)
def update_employee(employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db)):
    employee = get_employee_or_404(db, employee_id)
    updates = payload.model_dump(exclude_unset=True)
    if "department_id" in updates and updates["department_id"] is not None:
        validate_employee_department(db, updates["department_id"])
    for key, value in updates.items():
        setattr(employee, key, value)
    commit_or_conflict(db, "Employee with this name already exists in the department")
    return employee_read(get_employee_or_404(db, employee_id))


@router.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = get_employee_or_404(db, employee_id)
    if employee.tasks:
        raise HTTPException(status_code=409, detail="Cannot delete an employee who has tasks; deactivate the employee instead")
    if employee.projects:
        raise HTTPException(status_code=409, detail="Remove the employee from projects before deleting them")
    db.delete(employee)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/tasks", response_model=list[TaskRead])
def list_tasks(
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    priority: TaskPriority | None = None,
    employee_id: int | None = None,
    search: str | None = Query(default=None, max_length=200),
    project_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = select(Task).options(selectinload(Task.assigned_employee), selectinload(Task.project)).order_by(Task.created_at.desc(), Task.id.desc())
    if status_filter is not None:
        query = query.where(Task.status == status_filter)
    if priority is not None:
        query = query.where(Task.priority == priority)
    if employee_id is not None:
        query = query.where(Task.assigned_employee_id == employee_id)
    if project_id is not None:
        query = query.where(Task.project_id == project_id)
    if search:
        query = query.where(Task.title.ilike(f"%{search.strip()}%"))
    return [task_read(task) for task in db.scalars(query).all()]


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    validate_task_references(db, payload.assigned_employee_id, payload.project_id)
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    return task_read(get_task_or_404(db, task.id))


@router.get("/tasks/{task_id}", response_model=TaskRead)
def read_task(task_id: int, db: Session = Depends(get_db)):
    return task_read(get_task_or_404(db, task_id))


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = get_task_or_404(db, task_id)
    updates = payload.model_dump(exclude_unset=True)
    validate_task_references(db, updates.get("assigned_employee_id", task.assigned_employee_id), updates.get("project_id", task.project_id))
    for key, value in updates.items():
        setattr(task, key, value)
    db.commit()
    return task_read(get_task_or_404(db, task_id))


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db.delete(get_task_or_404(db, task_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(
    status_filter: ProjectStatus | None = Query(default=None, alias="status"),
    priority: TaskPriority | None = None,
    search: str | None = Query(default=None, max_length=160),
    db: Session = Depends(get_db),
):
    query = select(Project).options(selectinload(Project.employees), selectinload(Project.tasks)).order_by(Project.created_at.desc(), Project.id.desc())
    if status_filter is not None:
        query = query.where(Project.status == status_filter)
    if priority is not None:
        query = query.where(Project.priority == priority)
    if search:
        query = query.where(Project.name.ilike(f"%{search.strip()}%"))
    return [project_read(project) for project in db.scalars(query).all()]


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    values = payload.model_dump(exclude={"employee_ids"})
    employees = validate_project_employees(db, payload.employee_ids)
    project = Project(**values, employee_memberships=[ProjectEmployee(employee=employee) for employee in employees])
    db.add(project)
    db.commit()
    return project_read(get_project_or_404(db, project.id))


@router.get("/projects/{project_id}", response_model=ProjectRead)
def read_project(project_id: int, db: Session = Depends(get_db)):
    return project_read(get_project_or_404(db, project_id))


@router.patch("/projects/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id)
    updates = payload.model_dump(exclude_unset=True)
    if "employee_ids" in updates:
        employees = validate_project_employees(db, updates.pop("employee_ids"))
        project.employee_memberships = [ProjectEmployee(employee=employee) for employee in employees]
    for key, value in updates.items():
        setattr(project, key, value)
    if project.start_date and project.deadline and project.deadline < project.start_date:
        raise HTTPException(status_code=422, detail="deadline must not be earlier than start_date")
    db.commit()
    return project_read(get_project_or_404(db, project_id))


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id)
    if project.tasks:
        raise HTTPException(status_code=409, detail="Cannot delete a project while it has tasks; move or delete its tasks first")
    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
