import streamlit as st
from pymongo import MongoClient, errors
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# MongoDB connection
def connect_to_mongo():
    try:
        client = MongoClient("mongodb+srv://hananeassendal:RebelDehanane@cluster0.6bgmgnf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client.Newsapp
        return db.Users
    except errors.OperationFailure as e:
        st.error(f"Authentication failed: {e.details['errmsg']}")
    except errors.ServerSelectionTimeoutError as e:
        st.error(f"Server selection timeout: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    return None

users_collection = connect_to_mongo()

# Function to initialize session state
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False
    if 'page' not in st.session_state:
        st.session_state.page = 'login'  # Default to login page

# Function to send sign-up email notification
def send_signup_email(user_email):
    sender_email = "hananeassendal.info@gmail.com"
    receiver_email = "hananeassendal.info@gmail.com"
    password = "cbjf qqlx ueon ybjv"  # App Password

    message = MIMEMultipart("alternative")
    message["Subject"] = "New User Signup Notification"
    message["From"] = sender_email
    message["To"] = receiver_email

    base_url = "https://newsapport.streamlit.app/"
    validation_link = f"{base_url}/?validate={user_email}"
    
    text = f"A new user has signed up with the email: {user_email}\nPlease validate the user by clicking the link: {validation_link}"
    part = MIMEText(text, "plain")
    message.attach(part)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

# Function to send validation email to the user
def send_validation_email(user_email):
    sender_email = "hananeassendal.info@gmail.com"
    receiver_email = user_email
    password = "cbjf qqlx ueon ybjv"  # App Password

    message = MIMEMultipart("alternative")
    message["Subject"] = "Account Validation Successful"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"Your account with email {user_email} has been validated. You can now log in to the News App."
    part = MIMEText(text, "plain")
    message.attach(part)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

# Signup function
def signup():
    st.header("Sign Up")
    
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")

    countries = ["Brazil", "Dubai", "Saudi", "China"]
    country = st.selectbox("Select Country", countries, key="signup_country")
    
    if st.button("Sign Up"):
        if email and password and country:
            user = {"email": email, "password": password, "country": country, "validated": False}
            if users_collection is not None:
                try:
                    users_collection.insert_one(user)
                    send_signup_email(email)  # Send email notification to admin
                    st.success("Signup successful! Please check your email for validation.")
                    st.session_state.page = 'login'  # Redirect to login page
                except Exception as e:
                    st.error(f"Failed to sign up: {e}")
            else:
                st.error("Failed to connect to the database.")
        else:
            st.error("Please fill out all fields.")

# Login function
def login():
    st.header("Login")
    
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if email and password:
            if users_collection is not None:
                try:
                    user = users_collection.find_one({"email": email})
                    if user:
                        if user["password"] == password:
                            if user["validated"]:
                                st.session_state.logged_in = True
                                st.session_state.email = user["email"]
                                st.session_state.country = user.get("country", "")  # Store the country info if available
                                st.session_state.page = 'home'  # Redirect to home page
                            else:
                                st.error("Your account has not been validated yet. Please check your email for validation instructions.")
                        else:
                            st.error("Invalid password.")
                    else:
                        st.error("Invalid email or user not found.")
                except Exception as e:
                    st.error(f"Failed to log in: {e}")
            else:
                st.error("Failed to connect to the database.")
        else:
            st.error("Please fill out all fields.")

# Validation function
def validate_user(email):
    st.write(f"Validating user: {email}")
    if users_collection is not None:
        try:
            user = users_collection.find_one({"email": email})
            if user:
                result = users_collection.update_one({"email": email}, {"$set": {"validated": True}})
                if result.modified_count > 0:
                    send_validation_email(email)  # Send validation email to user
                    st.success("User validated successfully. The user has been notified via email.")
                else:
                    st.error("Failed to validate the user. Email not found.")
            else:
                st.error(f"Email {email} not found in the database.")
        except Exception as e:
            st.error(f"Failed to validate user: {e}")
    else:
        st.error("Failed to connect to the database.")

# Home function
def home():
    st.header("Welcome to the News App")
    st.write("This app provides the latest news articles based on your country.")
    st.write("You can also ask questions about any article you are interested in.")
    st.write("Navigate to the 'News' or 'Ask Me' sections from the menu.")

# Main function
def main():
    init_session_state()

    # Check if validation parameter is in URL
    query_params = st.experimental_get_query_params()
    if "validate" in query_params:
        email_to_validate = query_params["validate"][0]
        validate_user(email_to_validate)
    
    st.title("News App")

    if st.session_state.page == 'home':
        home()
    else:
        if st.session_state.logged_in:
            st.session_state.page = 'home'
        else:
            if st.session_state.show_signup:
                signup()
            else:
                login()
                if st.button("Go to Sign Up"):
                    st.session_state.show_signup = True

if __name__ == "__main__":
    main()
