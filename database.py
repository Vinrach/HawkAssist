import sqlite3
import csv

# Connect to the SQLite database (or create a new one if it doesn't exist)
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Create the tables
c.execute('''CREATE TABLE IF NOT EXISTS students
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS teachers
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS courses
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, teacher_id INTEGER, FOREIGN KEY(teacher_id) REFERENCES teachers(id))''')

c.execute('''CREATE TABLE IF NOT EXISTS course_materials
             (id INTEGER PRIMARY KEY AUTOINCREMENT, course_id INTEGER, material_link TEXT, FOREIGN KEY(course_id) REFERENCES courses(id))''')

c.execute('''CREATE TABLE IF NOT EXISTS enrollments
             (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, course_id INTEGER, FOREIGN KEY(student_id) REFERENCES students(id), FOREIGN KEY(course_id) REFERENCES courses(id))''')

c.execute('''CREATE TABLE IF NOT EXISTS tests
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, course_id INTEGER, FOREIGN KEY(course_id) REFERENCES courses(id))''')

c.execute('''CREATE TABLE IF NOT EXISTS test_results
             (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, test_id INTEGER, score INTEGER, FOREIGN KEY(student_id) REFERENCES students(id), FOREIGN KEY(test_id) REFERENCES tests(id))''')


# Insert data from CSV files into respective tables
def insert_data(table_name, csv_file):
    with open(csv_file, 'r') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)  # Skip the header row
        columns = ', '.join(header)
        placeholders = ', '.join('?' * len(header))
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        for row in csvreader:
            c.execute(insert_query, row)

# Function to update data in a table
def update_data(table_name, column_name, new_value, condition):
    update_query = f"UPDATE {table_name} SET {column_name} = ? WHERE {condition}"
    c.execute(update_query, (new_value,))
    conn.commit()
    print(f"Data updated in {table_name} table.")

# Function to delete data from a table
def delete_data(table_name, condition):
    delete_query = f"DELETE FROM {table_name} WHERE {condition}"
    c.execute(delete_query)
    conn.commit()
    print(f"Data deleted from {table_name} table.")








# Example usage: Update a student's age
update_data('students', 'age', 21, 'id = 1')

# Example usage: Delete a course material
delete_data('course_materials', 'id = 3')


# Call the insert_data function for each table
insert_data('students', 'students.csv')
insert_data('teachers', 'teachers.csv')
insert_data('courses', 'courses.csv')
insert_data('course_materials', 'course_materials.csv')
insert_data('enrollments', 'enrollments.csv')
insert_data('tests', 'tests.csv')
insert_data('test_results', 'test_results.csv')




# Commit the changes and close the connection
conn.commit()
conn.close()

print("Data imported successfully!")