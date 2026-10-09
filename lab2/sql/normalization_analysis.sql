-- ==============================================================================
-- DISCIPLINE: MANAGEMENT OF ORGANIZATIONAL DATA
-- LABORATORY WORK NO. 2: NORMALIZATION DECOMPOSITION & ANOMALY PROOFS
-- ==============================================================================

-- 1. INTENTIONALLY POORLY DESIGNED RELATION (UNF / FLAT SPREADSHEET TABLE)
DROP TABLE IF EXISTS hr_unf_monolith CASCADE;

CREATE TABLE hr_unf_monolith (
    emp_id INT,
    emp_name VARCHAR(100),
    emp_email VARCHAR(100),
    dept_id INT,
    dept_name VARCHAR(100),
    dept_manager VARCHAR(100),
    job_id INT,
    job_title VARCHAR(100),
    salary NUMERIC(12,2),
    proj_id INT,
    proj_name VARCHAR(100),
    proj_role VARCHAR(50),
    weekly_hours INT
);

-- Insert redundant, multi-valued, unnormalized rows
INSERT INTO hr_unf_monolith VALUES
(101, 'Didar Auyesbay', 'd.auyesbay@company.kz', 10, 'Software Engineering', 'Didar Auyesbay', 1, 'Lead Architect', 1250000.00, 501, 'HR Automation', 'Technical Lead', 20),
(101, 'Didar Auyesbay', 'd.auyesbay@company.kz', 10, 'Software Engineering', 'Didar Auyesbay', 1, 'Lead Architect', 1250000.00, 502, 'Core Banking', 'Consultant', 15),
(102, 'Aizhan Omarova', 'a.omarova@company.kz', 20, 'Human Resources', 'Aizhan Omarova', 3, 'HR Director', 850000.00, 501, 'HR Automation', 'Product Owner', 10),
(103, 'Arman Kasymov', 'a.kasymov@company.kz', 10, 'Software Engineering', 'Didar Auyesbay', 2, 'Senior Dev', 750000.00, 501, 'HR Automation', 'Backend Dev', 40),
(104, 'Dana Serikova', 'd.serikova@company.kz', 30, 'Finance', 'Dana Serikova', 5, 'Financial Analyst', 550000.00, 502, 'Core Banking', 'Auditor', 10);

-- ==============================================================================
-- 2. DEMONSTRATION OF RELATIONAL ANOMALIES ON UNNORMALIZED DATA
-- ==============================================================================

-- A. INSERTION ANOMALY:
-- Suppose a new department 'Cybersecurity' (dept_id: 40) is formed, or a new project 'Zero-Trust Architecture' (proj_id: 504) is approved.
-- In the monolith table with composite primary key (emp_id, proj_id), we CANNOT insert the department or project without hiring an employee and assigning them, because PK fields cannot be NULL!
-- SELECT 'Insertion Anomaly: Cannot insert project without employee into composite key table';

-- B. UPDATE ANOMALY:
-- If 'Software Engineering' is renamed to 'Software Engineering & AI', we must update multiple records.
-- If an update only modifies one row, data becomes inconsistent:
-- UPDATE hr_unf_monolith SET dept_name = 'Software Engineering & AI' WHERE emp_id = 101 AND proj_id = 501;
-- Result: Employee 101 has two conflicting department names across different project rows!

-- C. DELETION ANOMALY:
-- If Dana Serikova (emp_id 104) resigns or finishes project 502, deleting her row:
-- DELETE FROM hr_unf_monolith WHERE emp_id = 104;
-- Result: The Finance department, its manager, and its entire organizational existence are wiped out from the company records!

-- ==============================================================================
-- 3. VERIFICATION QUERY ON 3NF DATABASE (ANOMALIES COMPLETELY ELIMINATED)
-- ==============================================================================
-- In 3NF:
-- A department exists independently in departments table (No Insertion Anomaly).
-- Department name exists in exactly one row in departments table (No Update Anomaly).
-- Deleting an employee does NOT delete their department (No Deletion Anomaly).
