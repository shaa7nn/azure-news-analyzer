employees = []  

def add_employee():
    emp_id = input("Enter Employee ID: ")
    name = input("Enter Name: ")
    dept = input("Enter Department: ")
    salary = float(input("Enter Salary: "))

    emp = {
        "id": emp_id,
        "name": name,
        "dept": dept,
        "salary": salary,
        "details": (emp_id, name, dept, salary)  
    }

    employees.append(emp)
    print("Employee added successfully.\n")

def search_employee():
    key = input("Enter Employee ID or Name to search: ")
    found = False

    for emp in employees:
        if emp["id"] == key or emp["name"].lower() == key.lower():
            print("\nEmployee Found:")
            print("ID:", emp["id"])
            print("Name:", emp["name"])
            print("Department:", emp["dept"])
            print("Salary:", emp["salary"])
            found = True
            break

    if not found:
        print("Employee not found.\n")

def display_all_employees():
    if not employees:
        print("No employee records available.\n")
        return

    print("\nAll Employees:")
    for i, emp in enumerate(employees, start=1):   # iteration
        print(i, emp["id"], emp["name"], emp["dept"], emp["salary"])

    print("\nFirst Employee using indexing:")
    print(employees[0])

    print("\nFirst 2 Employees using slicing:")
    print(employees[:2])

    departments = set()
    for emp in employees:
        departments.add(emp["dept"])

    print("\nUnique Departments:")
    for dept in departments:
        print(dept)
    print()

while True:
    print("----- Employee Management System -----")
    print("1. Add Employee")
    print("2. Search Employee")
    print("3. Display All Employees")
    print("4. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        add_employee()
    elif choice == "2":
        search_employee()
    elif choice == "3":
        display_all_employees()
    elif choice == "4":
        print("Exiting program.")
        break
    else:
        print("Invalid choice. Try again.\n")