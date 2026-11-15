from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.db.models import EmployeeStatus, ProjectStatus, TaskPriority, TaskStatus


class CompanyConfigRead(BaseModel):
    id: int
    company_name: str
    product_name: str
    tagline: str
    industry: str
    market: str
    founder_role: str
    business_model: str

    model_config = ConfigDict(from_attributes=True)


class DepartmentBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=4000)


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=4000)


class DepartmentRead(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    employee_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class EmployeeBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    position: str = Field(min_length=1, max_length=120)
    department_id: int = Field(gt=0)
    description: str = Field(default="", max_length=4000)
    system_instructions: str = Field(default="", max_length=12000)
    ai_provider: str = Field(default="9router", min_length=1, max_length=80)
    ai_model: str = Field(default="", max_length=160)
    status: EmployeeStatus = EmployeeStatus.active


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    position: str | None = Field(default=None, min_length=1, max_length=120)
    department_id: int | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, max_length=4000)
    system_instructions: str | None = Field(default=None, max_length=12000)
    ai_provider: str | None = Field(default=None, min_length=1, max_length=80)
    ai_model: str | None = Field(default=None, max_length=160)
    status: EmployeeStatus | None = None


class EmployeeRead(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    department_name: str = ""

    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=8000)
    assigned_employee_id: int | None = Field(default=None, gt=0)
    project_id: int | None = Field(default=None, gt=0)
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.todo
    due_date: date | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=8000)
    assigned_employee_id: int | None = Field(default=None, gt=0)
    project_id: int | None = Field(default=None, gt=0)
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    due_date: date | None = None


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    assigned_employee_name: str | None = None
    project_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=8000)
    start_date: date | None = None
    deadline: date | None = None
    status: ProjectStatus = ProjectStatus.planned
    priority: TaskPriority = TaskPriority.medium
    employee_ids: list[int] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def dates_are_valid(self):
        if self.start_date and self.deadline and self.deadline < self.start_date:
            raise ValueError("deadline must not be earlier than start_date")
        if len(set(self.employee_ids)) != len(self.employee_ids):
            raise ValueError("employee_ids must not contain duplicates")
        return self


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=8000)
    start_date: date | None = None
    deadline: date | None = None
    status: ProjectStatus | None = None
    priority: TaskPriority | None = None
    employee_ids: list[int] | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def employee_ids_are_unique(self):
        if self.employee_ids is not None and len(set(self.employee_ids)) != len(self.employee_ids):
            raise ValueError("employee_ids must not contain duplicates")
        return self


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str
    start_date: date | None
    deadline: date | None
    status: ProjectStatus
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime
    employee_ids: list[int]
    employee_names: list[str]
    task_count: int
    completed_task_count: int
    progress_percent: int

    model_config = ConfigDict(from_attributes=True)


class DashboardStats(BaseModel):
    total_employees: int
    active_employees: int
    total_departments: int
    total_tasks: int
    completed_tasks: int
    ongoing_projects: int
