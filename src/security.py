import json

def read_db():
    try:
        with open('db/users.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def write_db(data):
    try:
        with open('db/users.json', 'w') as file:
            json.dump(data, file, indent=4)
        return True
    except FileNotFoundError:
        return False
        
def register(username, name, email, password, role="user"):
    try:
        data = read_db()

        if not data:
            return "Failed to register user", False
        
        for user in data:
            if user['username'] == username:
                return f"Username {username} already exists", False
            if user['email'] == email:
                return f"Email {email} already exists", False
        
        new_user = {
            "username": username,
            "name": name,
            "email": email,
            "password": password,
            "role": role
        }
        data.append(new_user)
        check = write_db(data)
        if check:
            return f"User {username} successfully registered", True
        else:
            return "Failed to register user", False
    except Exception as e:
        return str(e), False

def login(username, password):
    try:
        data = read_db()

        if not data:
            return "Failed to login", False
        
        for user in data:
            if user['username'] == username and user['password'] == password:
                return f"User {username} successfully logged in", True
        
        return "Invalid username or password", False
    except Exception as e:
        return str(e), False
    
def check_role(username):
    try:
        data = read_db()

        if not data:
            return "Failed to check role", False
        
        for user in data:
            if user['username'] == username:
                return user['role'], True
        
        return "User not found", False
    except Exception as e:
        return str(e), False
    
def change_password(username, old_password, new_password):
    try:
        data = read_db()

        if not data:
            return "Failed to change password", False
        
        for user in data:
            if user['username'] == username and user['password'] == old_password:
                user['password'] = new_password
                check = write_db(data)
                if check:
                    return f"Password successfully changed for user {username}", True
                else:
                    return "Failed to change password", False
        
        return "Invalid username or password", False
    except Exception as e:
        return str(e), False
    
def get_users():
    try:
        data = read_db()

        if not data:
            return "Failed to get users", False
        
        return data, True
    except Exception as e:
        return str(e), False
