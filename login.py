import streamlit as st
from captcha.image import ImageCaptcha
import random
import string
from pymongo import MongoClient, errors

# MongoDB connection
def connect_to_mongo():
    try:
        client = MongoClient("mongodb+srv://hananeassendal:RebelDehanane@cluster0.6bgmgnf.mongodb.net/Newsapp?retryWrites=true&w=majority&appName=Cluster0")
        db = client.Newsapp
        return db.Usersz
    except errors.PyMongoError as e:
        st.error("Error connecting to MongoDB: {}".format(e))
    return None

users_collection = connect_to_mongo()

# Define constants for CAPTCHA
LENGTH_CAPTCHA = 4
WIDTH = 200
HEIGHT = 100

# Function to initialize session state
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False
    if 'captcha_valid' not in st.session_state:
        st.session_state.captcha_valid = False

# Function to generate and display CAPTCHA
def generate_captcha():
    if 'captcha_text' not in st.session_state:
        st.session_state.captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=LENGTH_CAPTCHA))
    image = ImageCaptcha(width=WIDTH, height=HEIGHT)
    data = image.generate(st.session_state.captcha_text)
    st.image(data, caption='CAPTCHA Image')

# Signup function
def signup():
    st.header("Sign Up")
    
    captcha_input = st.text_input("Enter CAPTCHA")

    if 'captcha_text' not in st.session_state:
        generate_captcha()

    if st.button("Verify CAPTCHA"):
        if captcha_input == st.session_state.captcha_text:
            st.success("CAPTCHA verification successful!")
            st.session_state.captcha_valid = True
        else:
            st.error("CAPTCHA verification failed. Please try again.")
            generate_captcha()  # Regenerate CAPTCHA for another attempt

    if st.session_state.captcha_valid:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")

        countries = ["Brazil", "Dubai", "Saudi", "China"]
        country = st.selectbox("Select Country", countries, key="signup_country")

        if st.button("Sign Up"):
            if email and password and country:
                user = {"email": email, "password": password, "country": country}
                users_collection.insert_one(user)
                st.session_state.logged_in = True
                st.session_state.email = email
                st.session_state.country = country
                st.success("Sign-up successful!")
                st.experimental_rerun()  # Redirect to news page after sign-up
            else:
                st.error("Please fill out all fields.")

# Login function
def login():
    st.header("Login")

    captcha_input = st.text_input("Enter CAPTCHA")

    if 'captcha_text' not in st.session_state:
        generate_captcha()

    if st.button("Verify CAPTCHA"):
        if captcha_input == st.session_state.captcha_text:
            st.success("CAPTCHA verification successful!")
            st.session_state.captcha_valid = True
        else:
            st.error("CAPTCHA verification failed. Please try again.")
            generate_captcha()  # Regenerate CAPTCHA for another attempt

    if st.session_state.captcha_valid:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if email and password:
                user = users_collection.find_one({"email": email, "password": password})
                if user:
                    st.session_state.logged_in = True
                    st.session_state.email = user["email"]
                    st.session_state.country = user.get("country", "")  # Store the country info if available
                    st.success("Login successful!")
                    st.experimental_rerun()  # Redirect to news page after login
                else:
                    st.error("Invalid email or password.")
            else:
                st.error("Please fill out all fields and pass CAPTCHA verification.")

# Main function
def main():
    st.title("News App")
    init_session_state()

    if not st.session_state.logged_in:
        if st.session_state.show_signup:
            signup()
            if st.button("Go to Login"):
                st.session_state.show_signup = False
                st.experimental_rerun()
        else:
            login()
            if st.button("Go to Sign Up"):
                st.session_state.show_signup = True
                st.experimental_rerun()
    else:
        st.header("Welcome to the News App")
        st.write("[Go to News](news.py)")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.country = ""  # Clear country info on logout
            st.experimental_rerun()

if _name_ == "_main_":
    main()
