from datetime import date, datetime
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SqlEnum, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class EmployeeStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    busy = "busy"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    review = "review"
    completed = "completed"
    cancelled = "cancelled"


class ProjectStatus(str, Enum):
    planned = "planned"
    active = "active"
    on_hold = "on_hold"
    completed = "completed"
    cancelled = "cancelled"


class Department(Base):
    __tablename__ = "departments"
    __table_args__ = (UniqueConstraint("name", name="uq_departments_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    employees: Mapped[list["Employee"]] = relationship(back_populates="department", passive_deletes=True)


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (UniqueConstraint("name", "department_id", name="uq_employees_name_department"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    position: Mapped[str] = mapped_column(String(120), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    system_instructions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    ai_provider: Mapped[str] = mapped_column(String(80), nullable=False, default="9router")
    ai_model: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    status: Mapped[EmployeeStatus] = mapped_column(SqlEnum(EmployeeStatus, native_enum=False, length=20), nullable=False, default=EmployeeStatus.active, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    department: Mapped[Department] = relationship(back_populates="employees")
    tasks: Mapped[list["Task"]] = relationship(back_populates="assigned_employee", passive_deletes=True)
    project_memberships: Mapped[list["ProjectEmployee"]] = relationship(back_populates="employee", cascade="all, delete-orphan")
    projects: Mapped[list["Project"]] = relationship(secondary="project_employees", back_populates="employees", viewonly=True)


class ProjectEmployee(Base):
    __tablename__ = "project_employees"
    __table_args__ = (UniqueConstraint("project_id", "employee_id", name="uq_project_employee"),)

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="RESTRICT"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    project: Mapped["Project"] = relationship(back_populates="employee_memberships")
    employee: Mapped["Employee"] = relationship(back_populates="project_memberships")


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (UniqueConstraint("name", name="uq_projects_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(SqlEnum(ProjectStatus, native_enum=False, length=20), nullable=False, default=ProjectStatus.planned, index=True)
    priority: Mapped[TaskPriority] = mapped_column(SqlEnum(TaskPriority, native_enum=False, length=20), nullable=False, default=TaskPriority.medium)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    employee_memberships: Mapped[list[ProjectEmployee]] = relationship(back_populates="project", cascade="all, delete-orphan")
    employees: Mapped[list[Employee]] = relationship(secondary="project_employees", back_populates="projects", viewonly=True)
    tasks: Mapped[list["Task"]] = relationship(back_populates="project", passive_deletes=True)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    assigned_employee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    priority: Mapped[TaskPriority] = mapped_column(SqlEnum(TaskPriority, native_enum=False, length=20), nullable=False, default=TaskPriority.medium, index=True)
    status: Mapped[TaskStatus] = mapped_column(SqlEnum(TaskStatus, native_enum=False, length=20), nullable=False, default=TaskStatus.todo, index=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    assigned_employee: Mapped[Employee | None] = relationship(back_populates="tasks")
    project: Mapped[Project | None] = relationship(back_populates="tasks")


class CompanyConfig(Base):
    __tablename__ = "company_config"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    company_name: Mapped[str] = mapped_column(String(120), default="Aivanta Labs")
    product_name: Mapped[str] = mapped_column(String(120), default="Aivanta OS")
    tagline: Mapped[str] = mapped_column(String(200), default="Intelligence. Innovation. Automation.")
    industry: Mapped[str] = mapped_column(String(120), default="Artificial Intelligence & Technology")
    market: Mapped[str] = mapped_column(String(80), default="Global")
    founder_role: Mapped[str] = mapped_column(String(80), default="Founder & CEO")
    business_model: Mapped[str] = mapped_column(String(160), default="AI & Software Agency + Digital Products")
