# Relational Normalization Walkthrough: HR Organizational Data Domain
**Course**: Management of Organizational Data  
**Student**: Didar Auyesbay | **ID**: 25MD0303 | **Domain**: Human Resources (HR)  

---

## 1. Unnormalized Form (UNF)

In typical legacy spreadsheets or unnormalized inputs, employee and project information is stored in a single monolithic structure with non-atomic attributes and repeating groups.

### UNF Schema
`UNF_HR_STAFF_PROJECT (emp_id, emp_name, emp_email, dept_id, dept_name, dept_manager, job_id, job_title, salary, {proj_id, proj_name, proj_role, weekly_hours})`

### Sample UNF Data Table

| emp_id | emp_name | emp_email | dept_id | dept_name | dept_manager | job_id | job_title | salary | Projects Assigned `{proj_id, proj_name, proj_role, weekly_hours}` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **101** | Didar Auyesbay | d.auyesbay@company.kz | 10 | Software Eng | Didar Auyesbay | 1 | Lead Architect | 1,250,000 | `(501, HR Portal, Tech Lead, 20), (502, Core Banking, Consultant, 15)` |
| **102** | Aizhan Omarova | a.omarova@company.kz | 20 | Human Resources | Aizhan Omarova | 3 | HR Director | 850,000 | `(501, HR Portal, Product Owner, 10)` |
| **103** | Arman Kasymov | a.kasymov@company.kz | 10 | Software Eng | Didar Auyesbay | 2 | Senior Dev | 750,000 | `(501, HR Portal, Backend Dev, 40)` |
| **104** | Dana Serikova | d.serikova@company.kz | 30 | Finance | Dana Serikova | 5 | Financial Analyst | 550,000 | `(502, Core Banking, Auditor, 10)` |

### Why UNF Fails:
1. **Non-Atomic Data**: `emp_name` packs both first and last names together.
2. **Repeating Groups**: Multiple project allocations are stored inside an array/list within a single row.
3. **Undefined Primary Key**: No scalar attribute or standard primary key can uniquely identify a row without awkward nested indexing.

---

## 2. Transformation to First Normal Form (1NF)

### 1NF Rules:
- All attribute values must be **atomic** (indivisible scalar values from their underlying domain).
- Repeating groups must be eliminated by flattening each project assignment into its own separate tuple.
- A primary key must be defined.

### 1NF Relational Structure
Composite Primary Key: `(emp_id, proj_id)`

`HR_STAFF_PROJECT_1NF (emp_id, proj_id, first_name, last_name, emp_email, dept_id, dept_name, dept_manager, job_id, job_title, salary, proj_name, proj_role, weekly_hours)`

### Sample 1NF Data Table

| emp_id [PK] | proj_id [PK] | first_name | last_name | emp_email | dept_id | dept_name | job_id | job_title | salary | proj_name | proj_role | weekly_hours |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **101** | **501** | Didar | Auyesbay | d.auyesbay@co.kz | 10 | Software Eng | 1 | Lead Architect | 1,250,000 | HR Portal | Tech Lead | 20 |
| **101** | **502** | Didar | Auyesbay | d.auyesbay@co.kz | 10 | Software Eng | 1 | Lead Architect | 1,250,000 | Core Banking | Consultant | 15 |
| **102** | **501** | Aizhan | Omarova | a.omarova@co.kz | 20 | HR | 3 | HR Director | 850,000 | HR Portal | Product Owner | 10 |
| **103** | **501** | Arman | Kasymov | a.kasymov@co.kz | 10 | Software Eng | 2 | Senior Dev | 750,000 | HR Portal | Backend Dev | 40 |
| **104** | **502** | Dana | Serikova | d.serikova@co.kz | 30 | Finance | 5 | Fin Analyst | 550,000 | Core Banking | Auditor | 10 |

### Critical Anomalies Remaining in 1NF:
- **Insertion Anomaly**: If a new project (e.g., `proj_id: 503`, "Cloud Migration") is approved but no employee is assigned yet, it **cannot be inserted** because `emp_id` is part of the primary key and cannot be `NULL` (Entity Integrity Constraint).
- **Update Anomaly**: If Didar's base salary changes, it must be updated across all project rows (501 and 502). If one row is missed, Didar has two conflicting salaries.
- **Deletion Anomaly**: If Dana Serikova (emp_id 104) resigns and her assignment to project 502 is deleted, her entire employee record, department information, and job title are erased from the company.

---

## 3. Transformation to Second Normal Form (2NF)

### 2NF Rules:
- Relation must be in **1NF**.
- **No Partial Functional Dependencies**: Every non-key attribute must be fully functionally dependent on the entire primary key, not a proper subset of it.

### Functional Dependency (FD) Analysis on 1NF:
Composite Primary Key: `{emp_id, proj_id}`

1. **Partial Dependency 1 (on `emp_id` alone)**:
   `emp_id → first_name, last_name, emp_email, dept_id, dept_name, dept_manager, job_id, job_title, salary`
2. **Partial Dependency 2 (on `proj_id` alone)**:
   `proj_id → proj_name`
3. **Full Functional Dependency (on full `{emp_id, proj_id}`)**:
   `{emp_id, proj_id} → proj_role, weekly_hours`

### Decomposition into 2NF:
We decompose the 1NF table into three separate relations:

1. **`EMPLOYEE_2NF`**:
   - Primary Key: `emp_id`
   - Attributes: `emp_id, first_name, last_name, emp_email, dept_id, dept_name, dept_manager, job_id, job_title, salary`
2. **`PROJECT_2NF`**:
   - Primary Key: `proj_id`
   - Attributes: `proj_id, project_name`
3. **`PROJECT_ASSIGNMENT_2NF`**:
   - Composite Primary Key: `(emp_id, proj_id)`
   - Foreign Keys: `emp_id REFERENCES EMPLOYEE_2NF`, `proj_id REFERENCES PROJECT_2NF`
   - Attributes: `role_in_project, weekly_hours`

### Anomalies Resolved in 2NF:
- Projects can be inserted independently without employees.
- Deleting an assignment does not delete the employee or project.

### Anomalies Remaining in 2NF:
**Transitive Dependencies persist** inside `EMPLOYEE_2NF`:
- `emp_id → dept_id`, and `dept_id → dept_name, dept_manager`. Therefore, `emp_id → dept_name` is transitive!
- `emp_id → job_id`, and `job_id → job_title`. Therefore, `emp_id → job_title` is transitive!

If all employees in "Finance" leave, deleting them deletes the Finance department and its manager!

---

## 4. Transformation to Third Normal Form (3NF)

### 3NF Rules:
- Relation must be in **2NF**.
- **No Transitive Functional Dependencies**: No non-key attribute can depend on the primary key through another non-key attribute ($X \to Y$ and $Y \to Z$).
- In Codd's words: *"Every non-key attribute must depend on the key, the whole key, and nothing but the key."*

### Decomposition into 3NF:
Extract transitive determinants (`dept_id` and `job_id`) into their own dedicated relations:

1. **`DEPARTMENTS`**:
   - Primary Key: `department_id`
   - Attributes: `dept_name [UK], location, budget, manager_id [FK]`
2. **`JOB_ROLES`**:
   - Primary Key: `job_id`
   - Attributes: `job_title [UK], min_salary, max_salary`
3. **`EMPLOYEES`**:
   - Primary Key: `employee_id`
   - Foreign Keys: `department_id REFERENCES DEPARTMENTS`, `job_id REFERENCES JOB_ROLES`
   - Attributes: `iin [UK], first_name, last_name, email [UK], phone, hire_date, birth_date, status, base_salary`
4. **`PROJECTS`**:
   - Primary Key: `project_id`
   - Attributes: `project_name [UK], start_date, end_date, priority, budget`
5. **`PROJECT_ASSIGNMENTS`**:
   - Primary Key: `assignment_id` (surrogate) or `(employee_id, project_id)`
   - Foreign Keys: `employee_id REFERENCES EMPLOYEES`, `project_id REFERENCES PROJECTS`
   - Attributes: `role_in_project, weekly_hours, assigned_date`

---

## 5. Summary of Anomaly Resolution

| Anomaly Type | Manifestation in UNF / 1NF | Resolution in 3NF |
| :--- | :--- | :--- |
| **Insertion Anomaly** | Cannot create a new department or project without hiring and assigning an employee. | `DEPARTMENTS` and `PROJECTS` have independent tables and can be inserted freely. |
| **Update Anomaly** | Changing a department name or job title requires modifying dozens of redundant employee rows. | Department and job metadata exist in exactly **one place**; updates require a single tuple update. |
| **Deletion Anomaly** | Deleting the last employee on a project or department destroys all company records of that entity. | `ON DELETE RESTRICT` protects master entities; only junction records are removed. |
