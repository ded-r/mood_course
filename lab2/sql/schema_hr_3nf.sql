-- ==============================================================================
-- DISCIPLINE: MANAGEMENT OF ORGANIZATIONAL DATA
-- LABORATORY WORK NO. 2: HR ORGANIZATIONAL DATA MODELING & 3NF SCHEMA
-- Student: Didar Auyesbay | Student ID: 25MD0303 | Group: Sat 13:00 - 16:00
-- ==============================================================================

-- Clean up existing tables in reverse dependency order
DROP VIEW IF EXISTS v_department_salary_expenditure CASCADE;
DROP VIEW IF EXISTS v_employee_project_allocation CASCADE;
DROP TABLE IF EXISTS payroll_records CASCADE;
DROP TABLE IF EXISTS performance_reviews CASCADE;
DROP TABLE IF EXISTS leave_requests CASCADE;
DROP TABLE IF EXISTS project_assignments CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS job_roles CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

-- ------------------------------------------------------------------------------
-- 1. DEPARTMENTS TABLE (1NF -> 3NF)
-- ------------------------------------------------------------------------------
CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(150) NOT NULL,
    budget NUMERIC(14, 2) NOT NULL CHECK (budget > 0),
    manager_id INT NULL -- Self-referential FK added after employees table creation
);

-- ------------------------------------------------------------------------------
-- 2. JOB_ROLES TABLE (Eliminates Transitive Dependencies from Employee)
-- ------------------------------------------------------------------------------
CREATE TABLE job_roles (
    job_id SERIAL PRIMARY KEY,
    job_title VARCHAR(100) NOT NULL UNIQUE,
    min_salary NUMERIC(12, 2) NOT NULL CHECK (min_salary > 0),
    max_salary NUMERIC(12, 2) NOT NULL,
    CONSTRAINT chk_salary_range CHECK (min_salary <= max_salary)
);

-- ------------------------------------------------------------------------------
-- 3. EMPLOYEES TABLE (Core Entity in 3NF)
-- ------------------------------------------------------------------------------
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    iin VARCHAR(12) NOT NULL UNIQUE CHECK (iin ~ '^[0-9]{12}$'),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    phone VARCHAR(25) NOT NULL,
    hire_date DATE NOT NULL DEFAULT CURRENT_DATE,
    birth_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'ON_LEAVE', 'TERMINATED')),
    base_salary NUMERIC(12, 2) NOT NULL CHECK (base_salary >= 85000.00), -- Above statutory minimum wage
    department_id INT NOT NULL REFERENCES departments(department_id) ON DELETE RESTRICT,
    job_id INT NOT NULL REFERENCES job_roles(job_id) ON DELETE RESTRICT,
    CONSTRAINT chk_legal_age CHECK (birth_date <= hire_date - INTERVAL '18 years')
);

-- Add Foreign Key for Department Manager
ALTER TABLE departments
    ADD CONSTRAINT fk_department_manager
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
    ON DELETE SET NULL;

-- ------------------------------------------------------------------------------
-- 4. PROJECTS TABLE (Eliminates Partial Dependency from Staff-Project)
-- ------------------------------------------------------------------------------
CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(120) NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM' CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    budget NUMERIC(14, 2) NOT NULL CHECK (budget >= 0),
    CONSTRAINT chk_project_dates CHECK (end_date >= start_date)
);

-- ------------------------------------------------------------------------------
-- 5. PROJECT_ASSIGNMENTS TABLE (Resolves M:N Relationship)
-- ------------------------------------------------------------------------------
CREATE TABLE project_assignments (
    assignment_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    project_id INT NOT NULL REFERENCES projects(project_id) ON DELETE RESTRICT,
    role_in_project VARCHAR(50) NOT NULL,
    weekly_hours INT NOT NULL CHECK (weekly_hours BETWEEN 1 AND 40),
    assigned_date DATE NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT uq_employee_project UNIQUE (employee_id, project_id)
);

-- ------------------------------------------------------------------------------
-- 6. LEAVE_REQUESTS TABLE (Employee 1:N Leave Requests)
-- ------------------------------------------------------------------------------
CREATE TABLE leave_requests (
    leave_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    leave_type VARCHAR(20) NOT NULL CHECK (leave_type IN ('VACATION', 'SICK', 'PERSONAL', 'UNPAID')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
    approver_id INT NULL REFERENCES employees(employee_id) ON DELETE SET NULL,
    CONSTRAINT chk_leave_dates CHECK (end_date >= start_date)
);

-- ------------------------------------------------------------------------------
-- 7. PERFORMANCE_REVIEWS TABLE (Periodic Review Records)
-- ------------------------------------------------------------------------------
CREATE TABLE performance_reviews (
    review_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    reviewer_id INT NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    review_cycle VARCHAR(20) NOT NULL, -- e.g., '2026-Q1'
    review_date DATE NOT NULL DEFAULT CURRENT_DATE,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    feedback TEXT NOT NULL,
    CONSTRAINT uq_employee_cycle UNIQUE (employee_id, review_cycle)
);

-- ------------------------------------------------------------------------------
-- 8. PAYROLL_RECORDS TABLE (Statutory Payroll & Auditing)
-- ------------------------------------------------------------------------------
CREATE TABLE payroll_records (
    payroll_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    pay_period VARCHAR(7) NOT NULL CHECK (pay_period ~ '^[0-9]{4}-(0[1-9]|1[0-2])$'), -- YYYY-MM
    payment_date DATE NOT NULL,
    gross_pay NUMERIC(12, 2) NOT NULL CHECK (gross_pay > 0),
    tax_deduction NUMERIC(12, 2) NOT NULL CHECK (tax_deduction >= 0),
    net_pay NUMERIC(12, 2) NOT NULL CHECK (net_pay > 0),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PROCESSED', 'FAILED')),
    CONSTRAINT chk_net_gross CHECK (net_pay <= gross_pay),
    CONSTRAINT uq_employee_pay_period UNIQUE (employee_id, pay_period)
);

-- ------------------------------------------------------------------------------
-- INDEXES FOR HIGH-THROUGHPUT QUERY OPTIMIZATION
-- ------------------------------------------------------------------------------
CREATE INDEX idx_employees_department ON employees(department_id);
CREATE INDEX idx_employees_job ON employees(job_id);
CREATE INDEX idx_employees_email ON employees(email);
CREATE INDEX idx_assignments_employee ON project_assignments(employee_id);
CREATE INDEX idx_assignments_project ON project_assignments(project_id);
CREATE INDEX idx_payroll_employee ON payroll_records(employee_id);

-- ------------------------------------------------------------------------------
-- REPORTING VIEWS
-- ------------------------------------------------------------------------------
CREATE VIEW v_employee_project_allocation AS
SELECT 
    e.employee_id,
    e.first_name || ' ' || e.last_name AS employee_name,
    d.dept_name,
    j.job_title,
    p.project_name,
    pa.role_in_project,
    pa.weekly_hours,
    p.priority
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN job_roles j ON e.job_id = j.job_id
JOIN project_assignments pa ON e.employee_id = pa.employee_id
JOIN projects p ON pa.project_id = p.project_id;

CREATE VIEW v_department_salary_expenditure AS
SELECT 
    d.department_id,
    d.dept_name,
    COUNT(e.employee_id) AS total_employees,
    COALESCE(SUM(e.base_salary), 0) AS monthly_salary_spend,
    d.budget AS annual_operating_budget,
    ROUND((COALESCE(SUM(e.base_salary) * 12, 0) / d.budget) * 100, 2) AS budget_utilization_pct
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id AND e.status = 'ACTIVE'
GROUP BY d.department_id, d.dept_name, d.budget;
