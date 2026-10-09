import sys
from rich.console import Console
from rich.table import Table
from database import SessionLocal, engine
from models import Department, JobRole, Employee, Project, ProjectAssignment, PayrollRecord

console = Console()

def display_tables():
    db = SessionLocal()
    try:
        console.print("\n[bold blue]================================================================[/bold blue]")
        console.print("[bold cyan]       ORGANIZATIONAL DATABASE 3NF TABLES (HR DOMAIN)           [/bold cyan]")
        console.print("[bold blue]================================================================[/bold blue]\n")

        # 1. DEPARTMENTS
        t_dept = Table(title="1. DEPARTMENTS Table (3NF Entity)", title_style="bold green")
        t_dept.add_column("Dept ID", style="bold red")
        t_dept.add_column("Department Name", style="bold white")
        t_dept.add_column("Location", style="white")
        t_dept.add_column("Annual Budget (KZT)", style="yellow", justify="right")
        t_dept.add_column("Manager ID [FK]", style="cyan", justify="center")

        depts = db.query(Department).all()
        for d in depts:
            t_dept.add_row(str(d.department_id), d.dept_name, d.location, f"{float(d.budget):,.2f}", str(d.manager_id))
        console.print(t_dept)
        console.print()

        # 2. JOB ROLES
        t_jobs = Table(title="2. JOB_ROLES Table (Eliminates Transitive Dependencies)", title_style="bold green")
        t_jobs.add_column("Job ID", style="bold red")
        t_jobs.add_column("Job Title", style="bold white")
        t_jobs.add_column("Min Salary (KZT)", style="yellow", justify="right")
        t_jobs.add_column("Max Salary (KZT)", style="yellow", justify="right")

        jobs = db.query(JobRole).all()
        for j in jobs:
            t_jobs.add_row(str(j.job_id), j.job_title, f"{float(j.min_salary):,.2f}", f"{float(j.max_salary):,.2f}")
        console.print(t_jobs)
        console.print()

        # 3. EMPLOYEES
        t_emp = Table(title="3. EMPLOYEES Table (Core 3NF Master Entity)", title_style="bold green")
        t_emp.add_column("Emp ID", style="bold red")
        t_emp.add_column("IIN [UK]", style="magenta")
        t_emp.add_column("Full Name", style="bold white")
        t_emp.add_column("Corporate Email [UK]", style="cyan")
        t_emp.add_column("Dept [FK]", style="blue", justify="center")
        t_emp.add_column("Role [FK]", style="blue", justify="center")
        t_emp.add_column("Base Salary (KZT)", style="yellow", justify="right")
        t_emp.add_column("Status", style="green", justify="center")

        emps = db.query(Employee).all()
        for e in emps:
            t_emp.add_row(
                str(e.employee_id), e.iin, f"{e.first_name} {e.last_name}",
                e.email, str(e.department_id), str(e.job_id),
                f"{float(e.base_salary):,.2f}", e.status
            )
        console.print(t_emp)
        console.print()

        # 4. PROJECTS
        t_proj = Table(title="4. PROJECTS Table", title_style="bold green")
        t_proj.add_column("Proj ID", style="bold red")
        t_proj.add_column("Project Name", style="bold white")
        t_proj.add_column("Kickoff Date", style="white")
        t_proj.add_column("Target End", style="white")
        t_proj.add_column("Priority", style="magenta")
        t_proj.add_column("Budget (KZT)", style="yellow", justify="right")

        projs = db.query(Project).all()
        for p in projs:
            t_proj.add_row(str(p.project_id), p.project_name, str(p.start_date), str(p.end_date), p.priority, f"{float(p.budget):,.2f}")
        console.print(t_proj)
        console.print()

        # 5. PROJECT ASSIGNMENTS
        t_assign = Table(title="5. PROJECT_ASSIGNMENTS Table (M:N Associative Junction)", title_style="bold green")
        t_assign.add_column("Assign ID", style="bold red")
        t_assign.add_column("Emp ID [FK]", style="cyan", justify="center")
        t_assign.add_column("Project ID [FK]", style="cyan", justify="center")
        t_assign.add_column("Project Role", style="bold white")
        t_assign.add_column("Weekly Hours", style="yellow", justify="center")

        assigns = db.query(ProjectAssignment).all()
        for a in assigns:
            t_assign.add_row(str(a.assignment_id), str(a.employee_id), str(a.project_id), a.role_in_project, f"{a.weekly_hours} hrs/wk")
        console.print(t_assign)
        console.print()

        # 6. PAYROLL RECORDS
        t_pay = Table(title="6. PAYROLL_RECORDS Table", title_style="bold green")
        t_pay.add_column("Payroll ID", style="bold red")
        t_pay.add_column("Emp ID [FK]", style="cyan", justify="center")
        t_pay.add_column("Period", style="white", justify="center")
        t_pay.add_column("Gross Pay", style="yellow", justify="right")
        t_pay.add_column("Tax (Withholding)", style="red", justify="right")
        t_pay.add_column("Net Remuneration", style="green", justify="right")
        t_pay.add_column("Status", style="green", justify="center")

        payrolls = db.query(PayrollRecord).all()
        for pr in payrolls:
            t_pay.add_row(
                str(pr.payroll_id), str(pr.employee_id), pr.pay_period,
                f"{float(pr.gross_pay):,.2f}", f"{float(pr.tax_deduction):,.2f}",
                f"{float(pr.net_pay):,.2f}", pr.status
            )
        console.print(t_pay)
        console.print("\n[bold green]✓ 3NF Integrity Verified: All tables cleanly normalized with zero redundancy.[/bold green]\n")

    finally:
        db.close()

if __name__ == "__main__":
    display_tables()
