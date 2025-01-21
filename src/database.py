import psycopg2
from dotenv import load_dotenv
from src.logger import setup_logger
import os

load_dotenv()
logger = setup_logger(__name__)

def connect_database() -> tuple:
    """Function to connect to postgress database"""
    # Get the database url from the environment variables
    url = os.getenv('DATABASE_URL')
    if url is None:
        logger.error("No database url found")
        return "Could not connect to database.", False
    
    try:
        # Connect to the database
        connection = psycopg2.connect(url)
        cursor = connection.cursor()
        
        # Create the table if it does not exist
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255),
            password VARCHAR(255),
            role VARCHAR(255),
            api_calls INTEGER,
            total_token_count INTEGER
        );
        '''
        
        cursor.execute(create_table_query)
        connection.commit()
        
        logger.info("Connected to the database and ensured users table exists")
        # Return the connection object
        return connection, True
    except Exception as error:
        # Log the error and return the error message
        logger.error(f"Error connecting to database: {error}")
        return f"Unexpected error occurred: {error}", False
    
def register(username: str, name: str, email: str, password: str, role: str="user", api_calls: int=0, total_token_count: int=0) -> tuple:
    """Function to register a new user in the database"""
    try:
        # Connect to the database
        connection, success = connect_database()
        if not success:
            return connection, False  # This will be the error message

        cursor = connection.cursor()

        # Check if the user already exists
        check_user_query = '''
        SELECT * FROM users WHERE username = %s
        '''
        cursor.execute(check_user_query, (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            logger.warning(f"User with username {username} already exists")
            return "User with this username already exists", False

        # Create the insert query
        insert_query = '''
        INSERT INTO users (username, name, email, password, role, api_calls, total_token_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        
        # Execute the insert query
        cursor.execute(insert_query, (username, name, email, password, role, api_calls, total_token_count))
        connection.commit()

        logger.info(f"User {username} registered successfully")
        return "User registered successfully", True
    except Exception as error:
        # Log the error and return the error message
        logger.error(f"Error registering user: {error}")
        return f"Unexpected error occurred: {error}", False
    finally:
        # Close the connection
        cursor.close()
        connection.close()
    
def login(username: str, password: str) -> tuple:
    """Function to login a user in the application"""
    try:
        # Connect to the database
        connection, success = connect_database()
        if not success:
            return connection, False  # This will be the error message

        cursor = connection.cursor()
        
        # Check if the user already exists
        check_user_query = '''
        SELECT * FROM users WHERE username = %s
        '''
        cursor.execute(check_user_query, (username,))
        existing_user = cursor.fetchone()

        if not existing_user:
            logger.warning(f"User with username {username} does not exist")
            return "User with this username does not exist!", False
        
        # Validate the password
        stored_password = existing_user[3]  # Assuming password is the 4th column
        if stored_password != password:
            logger.warning(f"Incorrect password for user {username}")
            return "Incorrect password!", False
    
        logger.info(f"User {username} logged in successfully")
        return {
            'username': existing_user[0],
            'role': existing_user[4]        
        }, True
    except Exception as error:
        # Log the error and return the error message
        logger.error(f"Error logging in: {error}")
        return f"Unexpected error occurred: {error}", False
    finally:
        # Close the connection
        cursor.close()
        connection.close()
        

        connection.close()
        
def get_users() -> tuple:
    """Function to get all users from the database for admin"""
    try:
        # Connect to the database
        connection, success = connect_database()
        if not success:
            return connection, False  # This will be the error message

        cursor = connection.cursor()
        
        # Query to get all users
        get_users_query = '''
        SELECT * FROM users where role = 'user'
        '''
        cursor.execute(get_users_query)
        users = cursor.fetchall()

        all_users = []
        for user in users:
            user_data = {
                'username': user[0],
                'name': user[1],
                'email': user[2],
                'api_calls': user[5],
                'total_token_count': user[6]
            }
            all_users.append(user_data)
        
        logger.info("All users fetched successfully")
        return all_users, True
    except Exception as error:
        # Log the error and return None
        logger.error(f"Error fetching users: {error}")
        return f"Unexpected error occurred: {error}", False
    finally:
        # Close the connection
        cursor.close()
        connection.close()
        
def write_user_details(username: str, api_calls: int, total_token_count: int) -> tuple:
    """Function to update the user details in the database after processing the documents"""
    try:
        # Connect to the database
        connection, success = connect_database()
        if not success:
            return connection, False  # This will be the error message
        
        cursor = connection.cursor()
        
        # Query to get the user by username
        get_user_query = '''
        SELECT * FROM users WHERE username = %s
        '''
        cursor.execute(get_user_query, (username,))
        
        user = cursor.fetchone()
        
        if not user:
            logger.warning(f"User {username} not found")
            return "User not found", False
        
        # Fetch the existing values
        api_calls = user[5] + api_calls
        total_token_count = user[6] + total_token_count
        
        # Update the user details
        update_user_query = '''
        UPDATE users SET api_calls = %s, total_token_count = %s WHERE username = %s
        '''
        cursor.execute(update_user_query, (api_calls, total_token_count, username))
        connection.commit()
        
        logger.info(f"User {username} details updated successfully")
        return "User details updated successfully", True
    except Exception as error:
        # Log the error and return None
        logger.error(f"Error updating user details: {error}")
        return f"Unexpected error occurred: {error}", False
    finally:
        # Close the connection
        cursor.close()
        connection.close()
        
def check_role(username: str):
    """"Function to check the role of the user"""
    try:
        # Connect to the database
        connection, success = connect_database()
        if not success:
            return connection, False  # This will be the error message

        cursor = connection.cursor()
        
        # Query to get the user by username
        get_user_query = '''
        SELECT * FROM users WHERE username = %s
        '''
        cursor.execute(get_user_query, (username,))
        
        user = cursor.fetchone()
        
        if not user:
            logger.warning(f"User {username} not found")
            return "User not found", False
        
        logger.info(f"Role fetched successfully for user {username}")
        return user[4], True
    except Exception as error:
        # Log the error and return None
        logger.error(f"Error fetching role: {error}")
        return f"Unexpected error occurred: {error}", False
    finally:
        # Close the connection
        cursor.close()
        connection.close()
        
def change_password(username: str, old_password: str, new_password: str):
    """
    Function to change the password of the user
    """
    try:
        # Connect to the database
        connection, success = connect_database()
        if not success:
            return connection, False  # This will be the error message

        cursor = connection.cursor()
        
        # Query to get the user by username
        get_user_query = '''
        SELECT * FROM users WHERE username = %s
        '''
        cursor.execute(get_user_query, (username,))
        
        user = cursor.fetchone()
        
        if not user:
            logger.warning(f"User {username} not found")
            return "User not found", False
        
        # Validate the old password
        stored_password = user[3]  # Assuming password is the 4th column
        if stored_password != old_password:
            logger.warning(f"Incorrect old password for user {username}")
            return "Incorrect old password!", False
        
        # Update the password
        update_password_query = '''
        UPDATE users SET password = %s WHERE username = %s
        '''
        cursor.execute(update_password_query, (new_password, username))
        connection.commit()
        
        logger.info(f"Password changed successfully for user {username}")
        return "Password changed successfully", True
    except Exception as error:
        # Log the error and return the error message
        logger.error(f"Error changing password: {error}")
        return f"Unexpected error occurred: {error}", False
    finally:
        # Close the connection
        cursor.close()
        connection.close()
        
def get_config(username: str):
    """Function to get the total API calls and total token count for the user"""
    try:
        # Connect to the database
        connection, success = connect_database()
        if not success:
            return connection, False  # This will be the error message

        cursor = connection.cursor()
        
        # Query to get the user by username
        get_user_query = '''
        SELECT api_calls, total_token_count FROM users WHERE username = %s
        '''
        cursor.execute(get_user_query, (username,))
        
        user = cursor.fetchone()
        
        if not user:
            logger.warning(f"User {username} not found")
            return "User not found", False
        
        user_config = {
            'api_calls': user[0],
            'total_token_count': user[1]
        }
        
        logger.info(f"Config fetched successfully for user {username}")
        return user_config, True
    except Exception as error:
        # Log the error and return the error message
        logger.error(f"Error fetching config: {error}")
        return f"Unexpected error occurred: {error}", False
    finally:
        # Close the connection
        cursor.close()
        connection.close()