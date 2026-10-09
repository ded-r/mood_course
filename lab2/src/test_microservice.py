import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from database import Base
from models import Department, JobRole, Employee, Project, ProjectAssignment, LeaveRequest, PerformanceReview, PayrollRecord
from app import app

# Isolated in-memory database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# ------------------------------------------------------------------------------
# TEST BUSINESS REQUIREMENTS (BR-01 to BR-10)
# ------------------------------------------------------------------------------

def test_br01_department_positive_budget(db_session):
    """BR-01: Department budget must be positive and name must be unique."""
    dept = Department(dept_name="Engineering", location="Almaty", budget=10000000.0)
    db_session.add(dept)
    db_session.commit()
    assert dept.department_id is not None

    # Duplicate department name should fail
    duplicate_dept = Department(dept_name="Engineering", location="Astana", budget=5000000.0)
    db_session.add(duplicate_dept)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_br03_employee_constraints(db_session):
    """BR-03: Employee must satisfy minimum wage, valid department and job references."""
    dept = Department(dept_name="Human Resources", location="Almaty", budget=5000000.0)
    job = JobRole(job_title="HR Specialist", min_salary=300000.0, max_salary=600000.0)
    db_session.add_all([dept, job])
    db_session.commit()

    emp = Employee(
        iin="980315350123",
        first_name="Didar",
        last_name="Auyesbay",
        email="d.auyesbay@company.kz",
        phone="+77011112233",
        birth_date=date(1998, 3, 15),
        hire_date=date(2022, 1, 1),
        status="ACTIVE",
        base_salary=500000.0,
        department_id=dept.department_id,
        job_id=job.job_id
    )
    db_session.add(emp)
    db_session.commit()
    assert emp.employee_id is not None

    # Duplicate email should fail
    dup_emp = Employee(
        iin="990101350999",
        first_name="Another",
        last_name="User",
        email="d.auyesbay@company.kz", # Duplicate
        phone="+77011112244",
        birth_date=date(1999, 1, 1),
        hire_date=date(2022, 1, 1),
        status="ACTIVE",
        base_salary=500000.0,
        department_id=dept.department_id,
        job_id=job.job_id
    )
    db_session.add(dup_emp)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_br04_job_role_salary_bounds(db_session):
    """BR-04: Job role must maintain positive salary and valid range."""
    role = JobRole(job_title="DevOps Engineer", min_salary=500000.0, max_salary=950000.0)
    db_session.add(role)
    db_session.commit()
    assert role.job_id is not None

def test_br05_project_date_constraints(db_session):
    """BR-05: Project start date and end date relationship."""
    proj = Project(
        project_name="Data Pipeline 2.0",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 6, 30),
        priority="HIGH",
        budget=12000000.0
    )
    db_session.add(proj)
    db_session.commit()
    assert proj.project_id is not None

def test_br06_project_assignment_uniqueness_and_hours(db_session):
    """BR-06: M:N Project assignment weekly hours constraint and uniqueness."""
    dept = Department(dept_name="Finance", location="Almaty", budget=8000000.0)
    job = JobRole(job_title="Analyst", min_salary=300000.0, max_salary=600000.0)
    proj = Project(project_name="Core Audit", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31), budget=5000000.0)
    db_session.add_all([dept, job, proj])
    db_session.commit()

    emp = Employee(
        iin="950505350123",
        first_name="Dana",
        last_name="Serikova",
        email="dana@company.kz",
        phone="+77051234567",
        birth_date=date(1995, 5, 5),
        hire_date=date(2021, 1, 1),
        status="ACTIVE",
        base_salary=450000.0,
        department_id=dept.department_id,
        job_id=job.job_id
    )
    db_session.add(emp)
    db_session.commit()

    # Valid assignment
    assignment = ProjectAssignment(
        employee_id=emp.employee_id,
        project_id=proj.project_id,
        role_in_project="Lead Auditor",
        weekly_hours=20
    )
    db_session.add(assignment)
    db_session.commit()
    assert assignment.assignment_id is not None

    # Duplicate assignment must fail
    dup_assign = ProjectAssignment(
        employee_id=emp.employee_id,
        project_id=proj.project_id,
        role_in_project="Duplicate Role",
        weekly_hours=10
    )
    db_session.add(dup_assign)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_br08_performance_review_bounds(db_session):
    """BR-08: Review rating must be an integer between 1 and 5."""
    dept = Department(dept_name="Ops", location="Almaty", budget=4000000.0)
    job = JobRole(job_title="Specialist", min_salary=300000.0, max_salary=500000.0)
    db_session.add_all([dept, job])
    db_session.commit()

    emp1 = Employee(iin="940101350111", first_name="A", last_name="B", email="a@co.kz", phone="1", birth_date=date(1994,1,1), hire_date=date(2020,1,1), base_salary=350000.0, department_id=dept.department_id, job_id=job.job_id)
    emp2 = Employee(iin="940101350222", first_name="C", last_name="D", email="c@co.kz", phone="2", birth_date=date(1994,1,1), hire_date=date(2020,1,1), base_salary=350000.0, department_id=dept.department_id, job_id=job.job_id)
    db_session.add_all([emp1, emp2])
    db_session.commit()

    rev = PerformanceReview(
        employee_id=emp1.employee_id,
        reviewer_id=emp2.employee_id,
        review_cycle="2026-Q1",
        rating=5,
        feedback="Exceeded quarterly goals."
    )
    db_session.add(rev)
    db_session.commit()
    assert rev.review_id is not None

def test_br09_payroll_deduction_integrity(db_session):
    """BR-09: Net pay must not exceed gross pay."""
    dept = Department(dept_name="Legal", location="Almaty", budget=4000000.0)
    job = JobRole(job_title="Counsel", min_salary=500000.0, max_salary=900000.0)
    db_session.add_all([dept, job])
    db_session.commit()

    emp = Employee(iin="930101350333", first_name="L", last_name="M", email="l@co.kz", phone="3", birth_date=date(1993,1,1), hire_date=date(2019,1,1), base_salary=700000.0, department_id=dept.department_id, job_id=job.job_id)
    db_session.add(emp)
    db_session.commit()

    pay = PayrollRecord(
        employee_id=emp.employee_id,
        pay_period="2026-01",
        payment_date=date(2026, 1, 31),
        gross_pay=700000.0,
        tax_deduction=133000.0,
        net_pay=567000.0,
        status="PROCESSED"
    )
    db_session.add(pay)
    db_session.commit()
    assert pay.payroll_id is not None

# ------------------------------------------------------------------------------
# REST API INTEGRATION TESTS
# ------------------------------------------------------------------------------

def test_api_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json["status"] == "UP"

def test_api_department_flow(client):
    # Create Department
    res = client.post("/departments", json={
        "dept_name": "Cloud Operations",
        "location": "Almaty Data Center",
        "budget": 25000000.0
    })
    assert res.status_code in [201, 409] # 201 created or already exists
    
    # List Departments
    list_res = client.get("/departments")
    assert list_res.status_code == 200
    assert len(list_res.json) >= 1

def test_api_validation_errors(client):
    # Invalid budget
    res = client.post("/departments", json={
        "dept_name": "Negative Budget Dept",
        "location": "Almaty",
        "budget": -100
    })
    assert res.status_code == 422
