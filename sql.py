import sqlite3

# Connect to SQLite
connection = sqlite3.connect("EmployeesFromGithub.db")

# Create a cursor object
cursor = connection.cursor()

# Create the 'dept' table
cursor.execute("""
CREATE TABLE IF NOT EXISTS dept (
   DEPTNO INTEGER NOT NULL PRIMARY KEY,
   DNAME VARCHAR(20) NOT NULL,
   LOC VARCHAR(20) NOT NULL
);
""")

# Insert records into the 'dept' table
cursor.executemany("""
INSERT INTO dept (DEPTNO, DNAME, LOC) VALUES (?, ?, ?);
""", [
    (10, 'ACCOUNTING', 'NEW YORK'),
    (20, 'RESEARCH', 'DALLAS'),
    (30, 'SALES', 'CHICAGO'),
    (40, 'OPERATIONS', 'BOSTON')
])

# Create the 'emp' table
cursor.execute("""
CREATE TABLE IF NOT EXISTS emp (
   EMPNO INTEGER NOT NULL PRIMARY KEY,
   ENAME VARCHAR(20) NOT NULL,
   JOB VARCHAR(20) NOT NULL,
   MGR INTEGER,
   HIREDATE DATE NOT NULL,
   SAL INTEGER NOT NULL,
   COMM INTEGER,
   DEPTNO INTEGER NOT NULL,
   FOREIGN KEY (MGR) REFERENCES emp (EMPNO) ON DELETE SET NULL ON UPDATE CASCADE,
   FOREIGN KEY (DEPTNO) REFERENCES dept (DEPTNO) ON DELETE RESTRICT
);
""")

# Insert records into the 'emp' table
cursor.executemany("""
INSERT INTO emp (EMPNO, ENAME, JOB, MGR, HIREDATE, SAL, COMM, DEPTNO) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
""", [
    (7839, 'KING', 'PRESIDENT', None, '1981-11-17', 5000, None, 10),
    (7698, 'BLAKE', 'MANAGER', 7839, '1981-05-01', 2850, None, 30),
    (7654, 'MARTIN', 'SALESMAN', 7698, '1981-09-28', 1250, 1400, 30),
    # Add other employees similarly...
])

# Create the 'proj' table
cursor.execute("""
CREATE TABLE IF NOT EXISTS proj (
   PROJID INTEGER NOT NULL PRIMARY KEY,
   EMPNO INTEGER NOT NULL,
   STARTDATE DATE NOT NULL,
   ENDDATE DATE NOT NULL,
   FOREIGN KEY (EMPNO) REFERENCES emp (EMPNO) ON DELETE NO ACTION ON UPDATE CASCADE
);
""")

# Insert records into the 'proj' table
cursor.executemany("""
INSERT INTO proj (PROJID, EMPNO, STARTDATE, ENDDATE) VALUES (?, ?, ?, ?);
""", [
    (1, 7782, '2005-06-16', '2005-06-18'),
    (4, 7782, '2005-06-19', '2005-06-24'),
    # Add other projects similarly...
])

# Display all departments
print("Departments:")
dept_data = cursor.execute("SELECT * FROM dept")
for row in dept_data:
    print(row)

# Display all employees
print("\nEmployees:")
emp_data = cursor.execute("SELECT * FROM emp")
for row in emp_data:
    print(row)

# Display all projects
print("\nProjects:")
proj_data = cursor.execute("SELECT * FROM proj")
for row in proj_data:
    print(row)

# Commit changes and close connection
connection.commit()
connection.close()
