from datetime import date
from database import SessionLocal, Base, engine
from models import Department, JobRole, Employee, Project, ProjectAssignment, LeaveRequest, PerformanceReview, PayrollRecord

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if already fully seeded
        if db.query(Employee).count() >= 5:
            print("Database is already seeded with records.")
            return

        print("Seeding database with HR organizational master records...")

        # 1. Job Roles
        roles = [
            JobRole(job_id=1, job_title="Lead Software Architect", min_salary=850000.0, max_salary=1600000.0),
            JobRole(job_id=2, job_title="Senior Software Engineer", min_salary=650000.0, max_salary=1200000.0),
            JobRole(job_id=3, job_title="HR Director", min_salary=700000.0, max_salary=1300000.0),
            JobRole(job_id=4, job_title="HR Generalist", min_salary=300000.0, max_salary=550000.0),
            JobRole(job_id=5, job_title="Financial Analyst", min_salary=400000.0, max_salary=750000.0),
        ]
        db.add_all(roles)
        db.commit()

        # 2. Departments
        depts = [
            Department(department_id=10, dept_name="Software Engineering", location="Almaty Tech Hub, Block B", budget=150000000.0),
            Department(department_id=20, dept_name="Human Resources", location="Almaty Central HQ, Floor 2", budget=45000000.0),
            Department(department_id=30, dept_name="Finance & Accounting", location="Almaty Central HQ, Floor 3", budget=60000000.0),
        ]
        db.add_all(depts)
        db.commit()

        # 3. Employees
        employees = [
            Employee(
                employee_id=101, iin="980315350123", first_name="Didar", last_name="Auyesbay",
                email="d.auyesbay@company.kz", phone="+77011112233", hire_date=date(2022, 3, 1),
                birth_date=date(1998, 3, 15), status="ACTIVE", base_salary=1250000.0,
                department_id=10, job_id=1
            ),
            Employee(
                employee_id=102, iin="950821450678", first_name="Aizhan", last_name="Omarova",
                email="a.omarova@company.kz", phone="+77022223344", hire_date=date(2021, 6, 15),
                birth_date=date(1995, 8, 21), status="ACTIVE", base_salary=850000.0,
                department_id=20, job_id=3
            ),
            Employee(
                employee_id=103, iin="990510350890", first_name="Arman", last_name="Kasymov",
                email="a.kasymov@company.kz", phone="+77033334455", hire_date=date(2023, 1, 10),
                birth_date=date(1999, 5, 10), status="ACTIVE", base_salary=750000.0,
                department_id=10, job_id=2
            ),
            Employee(
                employee_id=104, iin="971104450112", first_name="Dana", last_name="Serikova",
                email="d.serikova@company.kz", phone="+77044445566", hire_date=date(2022, 9, 1),
                birth_date=date(1997, 11, 4), status="ACTIVE", base_salary=550000.0,
                department_id=30, job_id=5
            ),
            Employee(
                employee_id=105, iin="010214350999", first_name="Nurlan", last_name="Toleubek",
                email="n.toleubek@company.kz", phone="+77055556677", hire_date=date(2024, 2, 1),
                birth_date=date(2001, 2, 14), status="ACTIVE", base_salary=350000.0,
                department_id=20, job_id=4
            ),
        ]
        db.add_all(employees)
        db.commit()

        # Update department managers
        d10 = db.query(Department).filter_by(department_id=10).first()
        d20 = db.query(Department).filter_by(department_id=20).first()
        d30 = db.query(Department).filter_by(department_id=30).first()
        d10.manager_id = 101
        d20.manager_id = 102
        d30.manager_id = 104
        db.commit()

        # 4. Projects
        projects = [
            Project(project_id=501, project_name="HR Automation & Self-Service Portal", start_date=date(2026, 1, 15), end_date=date(2026, 7, 30), priority="HIGH", budget=18000000.0),
            Project(project_id=502, project_name="Core Banking Data Pipeline", start_date=date(2025, 11, 1), end_date=date(2026, 10, 31), priority="CRITICAL", budget=55000000.0),
            Project(project_id=503, project_name="Internal Security Audit 2026", start_date=date(2026, 2, 1), end_date=date(2026, 5, 31), priority="MEDIUM", budget=8000000.0),
        ]
        db.add_all(projects)
        db.commit()

        # 5. Project Assignments (M:N)
        assignments = [
            ProjectAssignment(assignment_id=1, employee_id=101, project_id=501, role_in_project="Technical Lead", weekly_hours=20, assigned_date=date(2026, 1, 15)),
            ProjectAssignment(assignment_id=2, employee_id=101, project_id=502, role_in_project="Principal Consultant", weekly_hours=15, assigned_date=date(2026, 1, 15)),
            ProjectAssignment(assignment_id=3, employee_id=103, project_id=501, role_in_project="Backend Developer", weekly_hours=40, assigned_date=date(2026, 1, 20)),
            ProjectAssignment(assignment_id=4, employee_id=102, project_id=501, role_in_project="Product Owner", weekly_hours=10, assigned_date=date(2026, 1, 15)),
            ProjectAssignment(assignment_id=5, employee_id=104, project_id=502, role_in_project="Financial Auditor", weekly_hours=10, assigned_date=date(2026, 2, 1)),
        ]
        db.add_all(assignments)
        db.commit()

        # 6. Payroll Records
        payrolls = [
            PayrollRecord(payroll_id=1, employee_id=101, pay_period="2026-01", payment_date=date(2026, 1, 31), gross_pay=1250000.0, tax_deduction=237500.0, net_pay=1012500.0, status="PROCESSED"),
            PayrollRecord(payroll_id=2, employee_id=102, pay_period="2026-01", payment_date=date(2026, 1, 31), gross_pay=850000.0, tax_deduction=161500.0, net_pay=688500.0, status="PROCESSED"),
            PayrollRecord(payroll_id=3, employee_id=103, pay_period="2026-01", payment_date=date(2026, 1, 31), gross_pay=750000.0, tax_deduction=142500.0, net_pay=607500.0, status="PROCESSED"),
            PayrollRecord(payroll_id=4, employee_id=104, pay_period="2026-01", payment_date=date(2026, 1, 31), gross_pay=550000.0, tax_deduction=104500.0, net_pay=445500.0, status="PROCESSED"),
            PayrollRecord(payroll_id=5, employee_id=105, pay_period="2026-01", payment_date=date(2026, 1, 31), gross_pay=350000.0, tax_deduction=66500.0, net_pay=283500.0, status="PROCESSED"),
        ]
        db.add_all(payrolls)
        db.commit()

        print("Database successfully seeded with 3NF organizational data!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
