import os
import sys
from pathlib import Path

# Ensure lab2/src is in sys.path regardless of execution CWD
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import re
from datetime import date, datetime
from flask import Flask, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from database import engine, SessionLocal, Base
from models import Department, JobRole, Employee, Project, ProjectAssignment
from seed import seed_database

app = Flask(__name__)

# Initialize database schema and auto-seed if needed
Base.metadata.create_all(bind=engine)
try:
    seed_database()
except Exception as e:
    print(f"Seed note: {e}")

def is_valid_email(email: str) -> bool:
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.match(pattern, email))

def is_valid_iin(iin: str) -> bool:
    return bool(re.match(r"^[0-9]{12}$", iin))

@app.route("/", methods=["GET"])
def dashboard():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>HR Organizational Data Management Microservice</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
            body { background: #0F172A; color: #F8FAFC; padding: 24px; }
            .container { max-width: 1100px; margin: 0 auto; }
            header { border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }
            h1 { font-size: 22px; color: #38BDF8; }
            .badge { background: #166534; color: #86EFAC; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: bold; }
            .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
            .card { background: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 16px; text-align: center; }
            .card h3 { font-size: 13px; color: #94A3B8; text-transform: uppercase; margin-bottom: 6px; }
            .card p { font-size: 24px; font-weight: bold; color: #F1F5F9; }
            .section { background: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 20px; margin-bottom: 24px; }
            .section h2 { font-size: 16px; margin-bottom: 12px; color: #38BDF8; border-bottom: 1px solid #334155; padding-bottom: 8px; }
            .btn-group { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
            button { background: #0284C7; color: white; border: none; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500; transition: background 0.2s; }
            button:hover { background: #0369A1; }
            button.danger { background: #DC2626; }
            button.danger:hover { background: #B91C1C; }
            pre { background: #0B0F19; border: 1px solid #1E293B; border-radius: 6px; padding: 12px; font-size: 12px; color: #38BDF8; max-height: 280px; overflow-y: auto; white-space: pre-wrap; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
            th, td { border: 1px solid #334155; padding: 8px 12px; text-align: left; }
            th { background: #0F172A; color: #94A3B8; }
            tr:nth-child(even) { background: #182234; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div>
                    <h1>HR Organizational Data Management Microservice</h1>
                    <p style="color: #94A3B8; font-size: 13px; margin-top: 4px;">Laboratory Work № 2 &bull; Management of Organizational Data &bull; Didar Auyesbay (25MD0303)</p>
                </div>
                <div class="badge">● SERVICE ONLINE (PORT 5001)</div>
            </header>

            <div class="grid">
                <div class="card"><h3>Departments</h3><p>3</p></div>
                <div class="card"><h3>Job Roles</h3><p>5</p></div>
                <div class="card"><h3>Active Employees</h3><p>5</p></div>
                <div class="card"><h3>Live Projects</h3><p>3</p></div>
            </div>

            <div class="section">
                <h2>1. Interactive REST API Endpoint Demonstrator</h2>
                <div class="btn-group">
                    <button onclick="fetchApi('/health')">GET /health</button>
                    <button onclick="fetchApi('/employees')">GET /employees</button>
                    <button onclick="fetchApi('/departments')">GET /departments</button>
                    <button onclick="fetchApi('/job-roles')">GET /job-roles</button>
                    <button onclick="fetchApi('/projects')">GET /projects</button>
                    <button onclick="fetchApi('/analytics/department-salaries')">GET /analytics/department-salaries</button>
                    <button class="danger" onclick="testInvalidConstraint()">Test Invalid Input (422 Rejection)</button>
                </div>
                <div style="font-size: 12px; color: #94A3B8; margin-bottom: 6px;" id="endpoint-label">Click any button above to test real-time JSON responses:</div>
                <pre id="json-output">// Click a button above to execute live REST request...</pre>
            </div>

            <div class="section">
                <h2>2. 3NF Database Entities Quick View (Employees & Departments)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Emp ID</th>
                            <th>Full Name</th>
                            <th>National IIN</th>
                            <th>Corporate Email</th>
                            <th>Base Salary</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>101</td><td>Didar Auyesbay</td><td>980315350123</td><td>d.auyesbay@company.kz</td><td>1,250,000 KZT</td><td>ACTIVE</td></tr>
                        <tr><td>102</td><td>Aizhan Omarova</td><td>950821450678</td><td>a.omarova@company.kz</td><td>850,000 KZT</td><td>ACTIVE</td></tr>
                        <tr><td>103</td><td>Arman Kasymov</td><td>990510350890</td><td>a.kasymov@company.kz</td><td>750,000 KZT</td><td>ACTIVE</td></tr>
                        <tr><td>104</td><td>Dana Serikova</td><td>971104450112</td><td>d.serikova@company.kz</td><td>550,000 KZT</td><td>ACTIVE</td></tr>
                        <tr><td>105</td><td>Nurlan Toleubek</td><td>010214350999</td><td>n.toleubek@company.kz</td><td>350,000 KZT</td><td>ACTIVE</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            async function fetchApi(endpoint) {
                document.getElementById('endpoint-label').innerText = 'Executing: ' + endpoint;
                try {
                    const res = await fetch(endpoint);
                    const data = await res.json();
                    document.getElementById('json-output').innerText = JSON.stringify(data, null, 2);
                } catch (e) {
                    document.getElementById('json-output').innerText = 'Error: ' + e;
                }
            }

            async function testInvalidConstraint() {
                document.getElementById('endpoint-label').innerText = 'Testing constraint rejection: POST /departments with negative budget (-500)';
                try {
                    const res = await fetch('/departments', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ dept_name: 'Invalid Budget Dept', location: 'Almaty', budget: -500 })
                    });
                    const data = await res.json();
                    document.getElementById('json-output').innerText = 'HTTP Status: ' + res.status + '\\n' + JSON.stringify(data, null, 2);
                } catch (e) {
                    document.getElementById('json-output').innerText = 'Error: ' + e;
                }
            }
        </script>
    </body>
    </html>
    """
    return html, 200

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "UP",
        "service": "HR Organizational Data Management Microservice",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }), 200

# ------------------------------------------------------------------------------
# DEPARTMENTS ENDPOINTS
# ------------------------------------------------------------------------------
@app.route("/departments", methods=["POST"])
def create_department():
    data = request.get_json() or {}
    required = ["dept_name", "location", "budget"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: '{field}'"}), 400

    if float(data["budget"]) <= 0:
        return jsonify({"error": "Department budget must be strictly positive."}), 422

    db = SessionLocal()
    try:
        dept = Department(
            dept_name=data["dept_name"],
            location=data["location"],
            budget=data["budget"],
            manager_id=data.get("manager_id")
        )
        db.add(dept)
        db.commit()
        db.refresh(dept)
        return jsonify(dept.to_dict()), 201
    except IntegrityError as e:
        db.rollback()
        return jsonify({"error": "Department name must be unique or manager ID invalid."}), 409
    finally:
        db.close()

@app.route("/departments", methods=["GET"])
def list_departments():
    db = SessionLocal()
    try:
        depts = db.query(Department).all()
        return jsonify([d.to_dict() for d in depts]), 200
    finally:
        db.close()

# ------------------------------------------------------------------------------
# JOB ROLES ENDPOINTS
# ------------------------------------------------------------------------------
@app.route("/job-roles", methods=["POST"])
def create_job_role():
    data = request.get_json() or {}
    required = ["job_title", "min_salary", "max_salary"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: '{field}'"}), 400

    min_sal = float(data["min_salary"])
    max_sal = float(data["max_salary"])
    if min_sal <= 0 or min_sal > max_sal:
        return jsonify({"error": "Invalid salary bounds: min_salary must be > 0 and <= max_salary."}), 422

    db = SessionLocal()
    try:
        job = JobRole(
            job_title=data["job_title"],
            min_salary=min_sal,
            max_salary=max_sal
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return jsonify(job.to_dict()), 201
    except IntegrityError:
        db.rollback()
        return jsonify({"error": "Job role with this title already exists."}), 409
    finally:
        db.close()

@app.route("/job-roles", methods=["GET"])
def list_job_roles():
    db = SessionLocal()
    try:
        roles = db.query(JobRole).all()
        return jsonify([r.to_dict() for r in roles]), 200
    finally:
        db.close()

# ------------------------------------------------------------------------------
# EMPLOYEES ENDPOINTS
# ------------------------------------------------------------------------------
@app.route("/employees", methods=["POST"])
def create_employee():
    data = request.get_json() or {}
    required = ["iin", "first_name", "last_name", "email", "phone", "birth_date", "base_salary", "department_id", "job_id"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: '{field}'"}), 400

    if not is_valid_iin(data["iin"]):
        return jsonify({"error": "National IIN must be an exact 12-digit numeric string."}), 422

    if not is_valid_email(data["email"]):
        return jsonify({"error": "Invalid email format."}), 422

    base_salary = float(data["base_salary"])
    if base_salary < 85000.00:
        return jsonify({"error": "Salary violates statutory minimum wage (85,000 KZT)."}), 422

    birth = date.fromisoformat(data["birth_date"])
    hire = date.fromisoformat(data.get("hire_date", str(date.today())))
    age_at_hire = (hire - birth).days / 365.25
    if age_at_hire < 18:
        return jsonify({"error": "Employee must be at least 18 years of age at hire date."}), 422

    db = SessionLocal()
    try:
        # Check job salary grade conformance
        job = db.query(JobRole).filter(JobRole.job_id == data["job_id"]).first()
        if not job:
            return jsonify({"error": f"Job role with ID {data['job_id']} not found."}), 404

        if base_salary < float(job.min_salary) or base_salary > float(job.max_salary):
            return jsonify({
                "error": f"Base salary {base_salary} is outside job salary grade [{job.min_salary}, {job.max_salary}]."
            }), 422

        emp = Employee(
            iin=data["iin"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone=data["phone"],
            hire_date=hire,
            birth_date=birth,
            status=data.get("status", "ACTIVE"),
            base_salary=base_salary,
            department_id=data["department_id"],
            job_id=data["job_id"]
        )
        db.add(emp)
        db.commit()
        db.refresh(emp)
        return jsonify(emp.to_dict()), 201
    except IntegrityError as e:
        db.rollback()
        return jsonify({"error": "Unique constraint violation (duplicate IIN or email) or invalid department/job FK."}), 409
    finally:
        db.close()

@app.route("/employees", methods=["GET"])
def list_employees():
    db = SessionLocal()
    try:
        dept_id = request.args.get("department_id")
        query = db.query(Employee)
        if dept_id:
            query = query.filter(Employee.department_id == int(dept_id))
        employees = query.all()
        return jsonify([e.to_dict() for e in employees]), 200
    finally:
        db.close()

# ------------------------------------------------------------------------------
# PROJECTS & ASSIGNMENTS ENDPOINTS
# ------------------------------------------------------------------------------
@app.route("/projects", methods=["POST"])
def create_project():
    data = request.get_json() or {}
    required = ["project_name", "start_date", "end_date", "budget"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: '{field}'"}), 400

    start = date.fromisoformat(data["start_date"])
    end = date.fromisoformat(data["end_date"])
    if end < start:
        return jsonify({"error": "Project end_date must be on or after start_date."}), 422

    db = SessionLocal()
    try:
        proj = Project(
            project_name=data["project_name"],
            start_date=start,
            end_date=end,
            priority=data.get("priority", "MEDIUM"),
            budget=float(data["budget"])
        )
        db.add(proj)
        db.commit()
        db.refresh(proj)
        return jsonify(proj.to_dict()), 201
    except IntegrityError:
        db.rollback()
        return jsonify({"error": "Project name must be unique."}), 409
    finally:
        db.close()

@app.route("/projects", methods=["GET"])
def list_projects():
    db = SessionLocal()
    try:
        projects = db.query(Project).all()
        return jsonify([p.to_dict() for p in projects]), 200
    finally:
        db.close()

@app.route("/assignments", methods=["POST"])
def assign_employee_to_project():
    data = request.get_json() or {}
    required = ["employee_id", "project_id", "role_in_project", "weekly_hours"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: '{field}'"}), 400

    hours = int(data["weekly_hours"])
    if hours < 1 or hours > 40:
        return jsonify({"error": "Weekly hours allocation must be between 1 and 40."}), 422

    db = SessionLocal()
    try:
        assignment = ProjectAssignment(
            employee_id=int(data["employee_id"]),
            project_id=int(data["project_id"]),
            role_in_project=data["role_in_project"],
            weekly_hours=hours,
            assigned_date=date.today()
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return jsonify(assignment.to_dict()), 201
    except IntegrityError:
        db.rollback()
        return jsonify({"error": "Employee is already assigned to this project or invalid ID."}), 409
    finally:
        db.close()

# ------------------------------------------------------------------------------
# ANALYTICS ENDPOINT (3NF Cross-Table Aggregation)
# ------------------------------------------------------------------------------
@app.route("/analytics/department-salaries", methods=["GET"])
def department_salary_analytics():
    db = SessionLocal()
    try:
        results = db.query(
            Department.department_id,
            Department.dept_name,
            Department.budget,
            func.count(Employee.employee_id).label("headcount"),
            func.coalesce(func.sum(Employee.base_salary), 0).label("total_monthly_spend")
        ).outerjoin(
            Employee, (Department.department_id == Employee.department_id) & (Employee.status == "ACTIVE")
        ).group_by(Department.department_id, Department.dept_name, Department.budget).all()

        payload = []
        for r in results:
            annual_spend = float(r.total_monthly_spend) * 12
            budget = float(r.budget)
            utilization = (annual_spend / budget * 100) if budget > 0 else 0
            payload.append({
                "department_id": r.department_id,
                "dept_name": r.dept_name,
                "headcount": r.headcount,
                "monthly_spend_kzt": float(r.total_monthly_spend),
                "annualized_spend_kzt": annual_spend,
                "annual_budget_kzt": budget,
                "budget_utilization_pct": round(utilization, 2)
            })
        return jsonify(payload), 200
    finally:
        db.close()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print(f"  HR Microservice running at: http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
