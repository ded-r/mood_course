from datetime import date
from sqlalchemy import (
    Column, Integer, String, Numeric, Date, Text, ForeignKey,
    CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from database import Base

class Department(Base):
    __tablename__ = "departments"

    department_id = Column(Integer, primary_key=True, autoincrement=True)
    dept_name = Column(String(100), nullable=False, unique=True)
    location = Column(String(150), nullable=False)
    budget = Column(Numeric(14, 2), nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL", use_alter=True), nullable=True)

    __table_args__ = (
        CheckConstraint("budget > 0", name="chk_dept_budget_positive"),
    )

    # Relationships
    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")
    manager = relationship("Employee", foreign_keys=[manager_id], post_update=True)

    def to_dict(self):
        return {
            "department_id": self.department_id,
            "dept_name": self.dept_name,
            "location": self.location,
            "budget": float(self.budget),
            "manager_id": self.manager_id
        }


class JobRole(Base):
    __tablename__ = "job_roles"

    job_id = Column(Integer, primary_key=True, autoincrement=True)
    job_title = Column(String(100), nullable=False, unique=True)
    min_salary = Column(Numeric(12, 2), nullable=False)
    max_salary = Column(Numeric(12, 2), nullable=False)

    __table_args__ = (
        CheckConstraint("min_salary > 0", name="chk_min_salary_positive"),
        CheckConstraint("min_salary <= max_salary", name="chk_salary_range_valid"),
    )

    employees = relationship("Employee", back_populates="job_role")

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "job_title": self.job_title,
            "min_salary": float(self.min_salary),
            "max_salary": float(self.max_salary)
        }


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    iin = Column(String(12), nullable=False, unique=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(25), nullable=False)
    hire_date = Column(Date, nullable=False, default=date.today)
    birth_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="ACTIVE")
    base_salary = Column(Numeric(12, 2), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.department_id", ondelete="RESTRICT"), nullable=False)
    job_id = Column(Integer, ForeignKey("job_roles.job_id", ondelete="RESTRICT"), nullable=False)

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'ON_LEAVE', 'TERMINATED')", name="chk_employee_status_valid"),
        CheckConstraint("base_salary >= 85000.00", name="chk_minimum_wage_statutory"),
    )

    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    job_role = relationship("JobRole", back_populates="employees")
    assignments = relationship("ProjectAssignment", back_populates="employee", cascade="all, delete-orphan")
    leave_requests = relationship("LeaveRequest", back_populates="employee", foreign_keys="LeaveRequest.employee_id")
    reviews = relationship("PerformanceReview", back_populates="employee", foreign_keys="PerformanceReview.employee_id")
    payrolls = relationship("PayrollRecord", back_populates="employee")

    def to_dict(self):
        return {
            "employee_id": self.employee_id,
            "iin": self.iin,
            "full_name": f"{self.first_name} {self.last_name}",
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "hire_date": str(self.hire_date),
            "birth_date": str(self.birth_date),
            "status": self.status,
            "base_salary": float(self.base_salary),
            "department_id": self.department_id,
            "job_id": self.job_id
        }


class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String(120), nullable=False, unique=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    priority = Column(String(20), nullable=False, default="MEDIUM")
    budget = Column(Numeric(14, 2), nullable=False)

    __table_args__ = (
        CheckConstraint("priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="chk_project_priority"),
        CheckConstraint("end_date >= start_date", name="chk_project_dates_order"),
        CheckConstraint("budget >= 0", name="chk_project_budget_nonnegative"),
    )

    assignments = relationship("ProjectAssignment", back_populates="project")

    def to_dict(self):
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "start_date": str(self.start_date),
            "end_date": str(self.end_date),
            "priority": self.priority,
            "budget": float(self.budget)
        }


class ProjectAssignment(Base):
    __tablename__ = "project_assignments"

    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.project_id", ondelete="RESTRICT"), nullable=False)
    role_in_project = Column(String(50), nullable=False)
    weekly_hours = Column(Integer, nullable=False)
    assigned_date = Column(Date, nullable=False, default=date.today)

    __table_args__ = (
        CheckConstraint("weekly_hours >= 1 AND weekly_hours <= 40", name="chk_weekly_hours_bounds"),
        UniqueConstraint("employee_id", "project_id", name="uq_emp_project_assignment"),
    )

    employee = relationship("Employee", back_populates="assignments")
    project = relationship("Project", back_populates="assignments")

    def to_dict(self):
        return {
            "assignment_id": self.assignment_id,
            "employee_id": self.employee_id,
            "project_id": self.project_id,
            "role_in_project": self.role_in_project,
            "weekly_hours": self.weekly_hours,
            "assigned_date": str(self.assigned_date)
        }


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    leave_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    leave_type = Column(String(20), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    approver_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        CheckConstraint("leave_type IN ('VACATION', 'SICK', 'PERSONAL', 'UNPAID')", name="chk_leave_type"),
        CheckConstraint("status IN ('PENDING', 'APPROVED', 'REJECTED')", name="chk_leave_status"),
        CheckConstraint("end_date >= start_date", name="chk_leave_dates_valid"),
    )

    employee = relationship("Employee", back_populates="leave_requests", foreign_keys=[employee_id])
    approver = relationship("Employee", foreign_keys=[approver_id])


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False)
    review_cycle = Column(String(20), nullable=False)
    review_date = Column(Date, nullable=False, default=date.today)
    rating = Column(Integer, nullable=False)
    feedback = Column(Text, nullable=False)

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="chk_review_rating_1_to_5"),
        UniqueConstraint("employee_id", "review_cycle", name="uq_emp_review_cycle"),
    )

    employee = relationship("Employee", back_populates="reviews", foreign_keys=[employee_id])
    reviewer = relationship("Employee", foreign_keys=[reviewer_id])


class PayrollRecord(Base):
    __tablename__ = "payroll_records"

    payroll_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="RESTRICT"), nullable=False)
    pay_period = Column(String(7), nullable=False) # 'YYYY-MM'
    payment_date = Column(Date, nullable=False)
    gross_pay = Column(Numeric(12, 2), nullable=False)
    tax_deduction = Column(Numeric(12, 2), nullable=False)
    net_pay = Column(Numeric(12, 2), nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")

    __table_args__ = (
        CheckConstraint("gross_pay > 0", name="chk_gross_pay_positive"),
        CheckConstraint("tax_deduction >= 0", name="chk_tax_deduction_nonnegative"),
        CheckConstraint("net_pay > 0 AND net_pay <= gross_pay", name="chk_net_pay_valid"),
        CheckConstraint("status IN ('PENDING', 'PROCESSED', 'FAILED')", name="chk_payroll_status"),
        UniqueConstraint("employee_id", "pay_period", name="uq_emp_pay_period"),
    )

    employee = relationship("Employee", back_populates="payrolls")
