import psycopg2
import os
from configparser import ConfigParser


# Utility functions


def clear_screen():
    """
    Clears the console screen based on the operating system.
    """
    # Check the operating system
    if os.name == "posix":  # Linux or macOS
        _ = os.system("clear")
    else:  # Windows
        _ = os.system("cls")


def connect_to_db(
    host: str, database: str, user: str, password: str
) -> psycopg2.extensions.connection | None:
    """
    Establishes a connection to the PostgreSQL database.
    """
    connection = None
    # Attempt to connect to the database
    try:
        connection = psycopg2.connect(
            host=host, database=database, user=user, password=password
        )
        print("Connection to the database was successful.")
        return connection
    except psycopg2.Error as e:
        print(f"An error occurred while connecting to the database: {e}")
        return None


def close_connection(connection: psycopg2.extensions.connection):
    """
    Closes the database connection.
    """
    if connection:
        connection.close()
        print("Database connection closed.")


def config(
    filename: str = "database.ini", section: str = "postgresql"
) -> dict:
    """
    Reads database configuration from a file.
    from https://www.geeksforgeeks.org/postgresql/postgresql-connecting-to-the-database-using-python/
    """
    parser = ConfigParser()
    parser.read(filename)

    db_config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db_config[param[0]] = param[1]
    else:
        raise Exception(f"Section {section} not found in the {filename} file")

    return db_config


# Database operation functions


def getAllStudents(connection: psycopg2.extensions.connection):
    query = "SELECT * FROM students;"

    # Execute the query and fetch all results
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        # Print each row
        for row in rows:
            print(row)


def addStudent(
    connection: psycopg2.extensions.connection,
    first_name: str,
    last_name: str,
    email: str,
    enrollment_date: str,
):
    query = """
    INSERT INTO students (first_name, last_name, email, enrollment_date)
    VALUES (%s, %s, %s, %s);
    """

    # Execute the insert query
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                query, (first_name, last_name, email, enrollment_date)
            )
            # Commit the changes
            connection.commit()
            print("Student added successfully.")
        except psycopg2.Error as e:
            # Rollback in case of error
            connection.rollback()
            print(f"An error occurred while adding the student: {e}")


def updateStudentEmail(
    connection: psycopg2.extensions.connection, student_id: int, new_email: str
):
    query = """
    UPDATE students
    SET email = %s
    WHERE student_id = %s;
    """

    # Execute the update query
    with connection.cursor() as cursor:
        try:
            cursor.execute(query, (new_email, student_id))
            # Commit the changes
            connection.commit()
            print("Student email updated successfully.")
        except psycopg2.Error as e:
            # Rollback in case of error
            connection.rollback()
            print(f"An error occurred while updating the student email: {e}")


def deleteStudent(connection: psycopg2.extensions.connection, student_id: int):
    query = """
    DELETE FROM students
    WHERE student_id = %s;
    """

    with connection.cursor() as cursor:
        try:
            # Execute the delete query
            cursor.execute(query, (student_id,))
            # Commit the changes
            connection.commit()
            print("Student deleted successfully.")
        except psycopg2.Error as e:
            # Rollback in case of error
            connection.rollback()
            print(f"An error occurred while deleting the student: {e}")


# Handler functions for menu options


def handle_getAllStudents(connection):
    clear_screen()
    print("getAllStudents() selected.")
    getAllStudents(connection)


def handle_addStudent(connection):
    clear_screen()
    print("addStudent() selected.")

    # Get student details from user
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")
    enrollment_date = input("Enter enrollment date (YYYY-MM-DD): ")

    # Validate input is not empty
    if not first_name or not last_name or not email or not enrollment_date:
        print("All fields are required. Student not added.")
        return

    # Call the addStudent function
    addStudent(
        connection,
        first_name,
        last_name,
        email,
        enrollment_date,
    )


def handle_updateStudentEmail(connection):
    clear_screen()
    print("updateStudentEmail() selected.")

    # Get student ID and new email from user
    student_id = int(input("Enter student ID to update: "))
    new_email = input("Enter new email: ")

    # Validate input is not empty
    if not new_email:
        print("Email cannot be empty. Update not performed.")
        return

    # Call the updateStudentEmail function
    updateStudentEmail(connection, student_id, new_email)


def handle_deleteStudent(connection):
    clear_screen()
    print("deleteStudent() selected.")

    # Get student ID from user
    student_id = int(input("Enter student ID to delete: "))

    # Call the deleteStudent function
    deleteStudent(connection, student_id)


def main():

    # Read database configuration and connect to the database
    config_data = config()
    connection = connect_to_db(**config_data)

    if connection:
        option = None
        while option != "0":
            # clear the screen
            clear_screen()

            # Display the menu options
            print("Menu:")
            print("1. getAllStudents()")
            print("2. addStudent()")
            print("3. updateStudentEmail()")
            print("4. deleteStudent()")
            print("0. Exit")

            # Get user input
            option = input("Select an option: ")

            # Handle the selected option
            match option:
                case "1":  # getAllStudents
                    handle_getAllStudents(connection)
                    input("Press Enter to continue...")
                case "2":  # addStudent
                    handle_addStudent(connection)
                    input("Press Enter to continue...")
                case "3":  # updateStudentEmail
                    handle_updateStudentEmail(connection)
                    input("Press Enter to continue...")
                case "4":  # deleteStudent
                    handle_deleteStudent(connection)
                    input("Press Enter to continue...")
                case "0":  # Exit
                    print("Exiting the program.")
                case _:  # Invalid option
                    print("Invalid option. Please try again.")
                    input("Press Enter to continue...")

    close_connection(connection)


if __name__ == "__main__":
    main()
