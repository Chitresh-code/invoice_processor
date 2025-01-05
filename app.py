import streamlit as st
import os
import shutil  # Import shutil for directory removal
import pandas as pd
import json
from src.preprocess import pdf_to_image_dict
from src.ai import process_image_data
from src.postprocess import create_dataframe, save_dataframe_to_excel, get_config
from src.security import login, register, change_password, get_users, check_role
from streamlit_cookies_manager import EncryptedCookieManager

# Set the page configuration, including the title
st.set_page_config(page_title="Invoice Extractor", page_icon="📄", layout="centered")

# Initialize the cookie manager
cookies = EncryptedCookieManager(
    prefix="invoice_extractor_", 
    password="your_secret_password"  # Replace with your own secret password
)

if not cookies.ready():
    st.stop()

USERS_FILE = "db/users.json"

def read_app_state():
    with open(USERS_FILE, "r") as file:
        users = json.load(file)
        for user in users:
            if user["username"] == "admin" and user["role"] == "admin":
                return user.get("app_state", "enabled") == "enabled"
    return True

def write_app_state(enabled):
    with open(USERS_FILE, "r") as file:
        users = json.load(file)
    for user in users:
        if user["role"] == "admin":
            user["app_state"] = "enabled" if enabled else "disabled"
            break
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)

def toggle_app_state():
    if "app_enabled" not in st.session_state:
        st.session_state.app_enabled = read_app_state()

    st.session_state.app_enabled = not st.session_state.app_enabled
    write_app_state(st.session_state.app_enabled)
    st.success(f"App {'enabled' if st.session_state.app_enabled else 'disabled'} successfully!")

def admin_dashboard():
    st.title("Admin Dashboard")
    st.write(f"Welcome, {st.session_state.username}!")
    
    # Display the list of users
    st.write("List of Users:")
    users, result = get_users()
    if result:
        if users is not None:
            # Creating a DataFrame from the list of users
            user_df = pd.DataFrame(users)
            if 'app_state' in user_df.columns:
                user_df.drop(columns=["app_state"], inplace=True)
            st.dataframe(user_df)
    else:
        st.error(users)
    
    # Toggle app state
    if st.button("Toggle App State"):
        toggle_app_state()

def invoice_extractor():
    if "app_enabled" not in st.session_state:
        st.session_state.app_enabled = read_app_state()

    if not st.session_state.app_enabled:
        st.write("The app is currently not working as intended. Please contact the administrator for more information.")
        return

    st.write("Invoice Extractor Page")
    # File uploader for PDF files
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        # Create the tempDir directory if it doesn't exist
        temp_dir = "tempDir"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Save the uploaded file temporarily
        pdf_path = os.path.join(temp_dir, uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Convert PDF to image dictionary
        st.write("Converting PDF to images...")
        image_dict = pdf_to_image_dict(pdf_path)

        if image_dict is not None:
            # Process the image data to extract table information
            st.write("Processing images to extract table data...")
            processed_data = process_image_data(st.session_state.username, image_dict)

            if processed_data is not None:
                # Create a DataFrame from the processed data
                st.write("Creating DataFrame from extracted data...")
                df = create_dataframe(processed_data)

                if df is not None:
                    # Display the DataFrame
                    st.write("Extracted Data:")
                    st.dataframe(df)

                    # Save the DataFrame to an Excel file
                    excel_file_path = os.path.join(temp_dir, "extracted_data.xlsx")
                    save_dataframe_to_excel(df, excel_file_path)

                    # Check if the file was created successfully
                    if os.path.exists(excel_file_path):
                        # Provide a download link for the Excel file
                        st.download_button(
                            label="Download Excel File",
                            data=open(excel_file_path, "rb").read(),
                            file_name="extracted_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.error("Failed to create the Excel file.")
                else:
                    st.error("No valid data extracted from the images.")
            else:
                st.error("Failed to process image data.")
        else:
            st.error("Failed to convert PDF to images.")

        # Print the configuration data
        api_calls, token_count = get_config(st.session_state.username)
        if api_calls is not None and token_count is not None:
            st.write("Configuration Data:")
            st.write(f"Total API Calls by {st.session_state.username}: {api_calls}")
            st.write(f"Total Token Usage by {st.session_state.username}: {token_count}")
        else:
            st.error("Failed to get configuration data.")
        # Clean up temporary files if necessary
        shutil.rmtree(temp_dir)  # Remove the tempDir directory
        st.write("Temporary files cleaned up.")  # Log cleanup message

def user_login():
    st.title("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login", type="primary", use_container_width=True):
        message, result = login(username, password)
        if result:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "home"
            cookies["logged_in"] = "True"
            cookies["username"] = username
            cookies.save()
            st.rerun()
        else:
            st.error(message)

def user_sign_up():
    st.title("Register")
    username = st.text_input("Username", key="signup_username")
    name = st.text_input("Name", key="signup_name")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
    
    if password != confirm_password:
        st.error("Passwords do not match")
    
    if st.button("Register", type="primary", use_container_width=True):
        message, result = register(username, name, email, password)
        if result:
            return True
        else:
            st.error(message)
            
def change_user_password():
    st.title("Change Password")
    username = st.text_input("Username", key="change_username")
    old_password = st.text_input("Old Password", type="password", key="change_old_password")
    new_password = st.text_input("New Password", type="password", key="change_new_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="change_confirm_password")
    
    if new_password != confirm_password:
        st.error("Passwords do not match")
    
    if st.button("Change Password", type="primary", use_container_width=True):
        message, result = change_password(username, old_password, new_password)
        if result:
            st.session_state.page = "home"
            st.rerun()
        else:
            st.error(message)

def main():
    # Hide Streamlit menu and footer
    hide_menu_style = """
    <style>
    .stToolbarActions .stToolbarActionButton {
        visibility: hidden;
    }
    ._profileContainer_gzau3_53 {
        display: none;
    }
    </style>
    """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

    # Set the title of the Streamlit app
    st.title("PDF Invoice Processor")
    st.write("This app extracts table data from PDF invoices.")
    
    # Initialize session state for login status
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = cookies.get("logged_in", "False") == "True"
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    if 'username' not in st.session_state:
        st.session_state.username = cookies.get("username", "")
    if 'app_enabled' not in st.session_state:
        st.session_state.app_enabled = read_app_state()

    # Sidebar for navigation
    st.sidebar.title("User Authentication")
    if st.session_state.logged_in:
        if st.sidebar.button("Home", icon="🏠", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
        if st.sidebar.button("Change Password", icon="🔑", use_container_width=True):
            st.session_state.page = "change_password"
            st.rerun()
        if st.sidebar.button("Logout", icon="🔒", use_container_width=True):
            st.session_state.logged_in = False
            cookies["logged_in"] = "False"
            cookies["username"] = ""
            cookies.save()
            st.rerun()
        
        # Check user role and display appropriate dashboard
        role, status = check_role(st.session_state.username)
        if status:
            if role == "admin":
                if st.session_state.page == "home":
                    admin_dashboard()
                elif st.session_state.page == "change_password":
                    change_user_password()
            elif role == "user":
                if st.session_state.page == "home":
                    invoice_extractor()
                elif st.session_state.page == "change_password":
                    change_user_password()
        else:
            st.error("User not authenticated properly! Please login again and if the issue persists, try creating a new account.")
    else:
        if st.sidebar.button("Login", icon="🔑", use_container_width=True):
            st.session_state.auth_option = "Login"
        if st.sidebar.button("Register", icon="📝", use_container_width=True):
            st.session_state.auth_option = "Register"

        if 'auth_option' in st.session_state:
            if st.session_state.auth_option == "Login":
                user_login()
            elif st.session_state.auth_option == "Register":
                user_sign_up()

if __name__ == "__main__":
    main()