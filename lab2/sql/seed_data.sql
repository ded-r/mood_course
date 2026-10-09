-- ==============================================================================
-- DISCIPLINE: MANAGEMENT OF ORGANIZATIONAL DATA
-- LABORATORY WORK NO. 2: HR SEED DATA SCRIPT
-- ==============================================================================

-- 1. Insert Job Roles
INSERT INTO job_roles (job_id, job_title, min_salary, max_salary) VALUES
(1, 'Lead Software Architect', 850000.00, 1600000.00),
(2, 'Senior Software Engineer', 650000.00, 1200000.00),
(3, 'HR Director', 700000.00, 1300000.00),
(4, 'HR Generalist', 300000.00, 550000.00),
(5, 'Financial Analyst', 400000.00, 750000.00);

-- 2. Insert Departments (temporary NULL managers)
INSERT INTO departments (department_id, dept_name, location, budget, manager_id) VALUES
(10, 'Software Engineering', 'Almaty Tech Hub, Block B, Floor 4', 150000000.00, NULL),
(20, 'Human Resources', 'Almaty Central HQ, Floor 2', 45000000.00, NULL),
(30, 'Finance & Accounting', 'Almaty Central HQ, Floor 3', 60000000.00, NULL);

-- 3. Insert Employees
INSERT INTO employees (employee_id, iin, first_name, last_name, email, phone, hire_date, birth_date, status, base_salary, department_id, job_id) VALUES
(101, '980315350123', 'Didar', 'Auyesbay', 'd.auyesbay@company.kz', '+77011112233', '2022-03-01', '1998-03-15', 'ACTIVE', 1250000.00, 10, 1),
(102, '950821450678', 'Aizhan', 'Omarova', 'a.omarova@company.kz', '+77022223344', '2021-06-15', '1995-08-21', 'ACTIVE', 850000.00, 20, 3),
(103, '990510350890', 'Arman', 'Kasymov', 'a.kasymov@company.kz', '+77033334455', '2023-01-10', '1999-05-10', 'ACTIVE', 750000.00, 10, 2),
(104, '971104450112', 'Dana', 'Serikova', 'd.serikova@company.kz', '+77044445566', '2022-09-01', '1997-11-04', 'ACTIVE', 550000.00, 30, 5),
(105, '010214350999', 'Nurlan', 'Toleubek', 'n.toleubek@company.kz', '+77055556677', '2024-02-01', '2001-02-14', 'ACTIVE', 350000.00, 20, 4);

-- 4. Update Department Managers
UPDATE departments SET manager_id = 101 WHERE department_id = 10;
UPDATE departments SET manager_id = 102 WHERE department_id = 20;
UPDATE departments SET manager_id = 104 WHERE department_id = 30;

-- 5. Insert Projects
INSERT INTO projects (project_id, project_name, start_date, end_date, priority, budget) VALUES
(501, 'HR Automation & Self-Service Portal', '2026-01-15', '2026-07-30', 'HIGH', 18000000.00),
(502, 'Core Banking Data Pipeline', '2025-11-01', '2026-10-31', 'CRITICAL', 55000000.00),
(503, 'Internal Security Audit 2026', '2026-02-01', '2026-05-31', 'MEDIUM', 8000000.00);

-- 6. Insert Project Assignments (M:N junction)
INSERT INTO project_assignments (assignment_id, employee_id, project_id, role_in_project, weekly_hours, assigned_date) VALUES
(1, 101, 501, 'Technical Architect & Lead', 20, '2026-01-15'),
(2, 101, 502, 'Principal Consultant', 15, '2026-01-15'),
(3, 103, 501, 'Backend Developer', 40, '2026-01-20'),
(4, 102, 501, 'Product Owner / Domain Lead', 10, '2026-01-15'),
(5, 104, 502, 'Financial Auditor', 10, '2026-02-01');

-- 7. Insert Leave Requests
INSERT INTO leave_requests (leave_id, employee_id, leave_type, start_date, end_date, status, approver_id) VALUES
(1, 103, 'VACATION', '2026-07-01', '2026-07-14', 'APPROVED', 101),
(2, 105, 'SICK', '2026-03-03', '2026-03-05', 'APPROVED', 102);

-- 8. Insert Performance Reviews
INSERT INTO performance_reviews (review_id, employee_id, reviewer_id, review_cycle, review_date, rating, feedback) VALUES
(1, 103, 101, '2025-Q4', '2026-01-10', 5, 'Exceptional performance in optimizing microservice architecture and data pipelines.'),
(2, 105, 102, '2025-Q4', '2026-01-12', 4, 'Solid contributions to onboarding automation and document compliance.');

-- 9. Insert Payroll Records
INSERT INTO payroll_records (payroll_id, employee_id, pay_period, payment_date, gross_pay, tax_deduction, net_pay, status) VALUES
(1, 101, '2026-01', '2026-01-31', 1250000.00, 237500.00, 1012500.00, 'PROCESSED'),
(2, 102, '2026-01', '2026-01-31', 850000.00, 161500.00, 688500.00, 'PROCESSED'),
(3, 103, '2026-01', '2026-01-31', 750000.00, 142500.00, 607500.00, 'PROCESSED'),
(4, 104, '2026-01', '2026-01-31', 550000.00, 104500.00, 445500.00, 'PROCESSED'),
(5, 105, '2026-01', '2026-01-31', 350000.00, 66500.00, 283500.00, 'PROCESSED');
