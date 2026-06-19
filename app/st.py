import streamlit as st
import requests
from streamlit_cookies_manager import EncryptedCookieManager

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Research Agent",
    page_icon="🤖",
    layout="centered"
)

cookies = EncryptedCookieManager(
    prefix="research_agent_",
    password="your-very-secret-cookie-password"
)

if not cookies.ready():
    st.stop()


default_values = {
    "logged_in": False,
    "user_id": None,
    "username": None,
    "email": None,
    "access_token": None
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value


# Restore login after refresh
if cookies.get("access_token"):
    st.session_state.logged_in = True
    st.session_state.user_id = cookies.get("user_id")
    st.session_state.username = cookies.get("username")
    st.session_state.email = cookies.get("email")
    st.session_state.access_token = cookies.get("access_token")


def save_login_to_cookie(data):
    cookies["access_token"] = data["access_token"]
    cookies["user_id"] = data["user_id"]
    cookies["username"] = data["username"]
    cookies["email"] = data["email"]
    cookies.save()


def logout_user():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.email = None
    st.session_state.access_token = None

    for key in ["access_token", "user_id", "username", "email"]:
        if key in cookies:
            del cookies[key]

    cookies.save()


st.title("🤖 Research Agent")
st.write("FastAPI + LangGraph + Tavily + Groq + MongoDB Atlas")


if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    menu = st.sidebar.radio("Menu", ["Research", "Logout"])
else:
    menu = st.sidebar.radio("Menu", ["Login", "Sign Up"])


if menu == "Sign Up":
    st.subheader("Create Account")

    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up")

    if submit:
        if not username.strip() or not email.strip() or not password.strip():
            st.warning("Please fill all fields.")

        elif password != confirm_password:
            st.warning("Passwords do not match.")

        elif len(password) < 6:
            st.warning("Password must be at least 6 characters.")

        else:
            try:
                response = requests.post(
                    f"{BASE_URL}/signup",
                    json={
                        "username": username.strip(),
                        "email": email.strip(),
                        "password": password
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    st.success("Account created successfully!")
                    st.info(f"Your MongoDB User ID is: {data['user_id']}")
                    st.write("Now go to Login page.")
                else:
                    st.error("Sign up failed.")
                    st.code(response.text)

            except requests.exceptions.ConnectionError:
                st.error("FastAPI server is not running.")
                st.code("uvicorn app.main:app --reload")

            except Exception as error:
                st.error(f"Unexpected error: {error}")


elif menu == "Login":
    st.subheader("Login")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if not email.strip() or not password.strip():
            st.warning("Please enter email and password.")

        else:
            try:
                response = requests.post(
                    f"{BASE_URL}/login",
                    json={
                        "email": email.strip(),
                        "password": password
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()

                    st.session_state.logged_in = True
                    st.session_state.user_id = data["user_id"]
                    st.session_state.username = data["username"]
                    st.session_state.email = data["email"]
                    st.session_state.access_token = data["access_token"]

                    save_login_to_cookie(data)

                    st.success("Login successful!")
                    st.rerun()

                else:
                    st.error("Login failed.")
                    st.code(response.text)

            except requests.exceptions.ConnectionError:
                st.error("FastAPI server is not running.")
                st.code("uvicorn app.main:app --reload")

            except Exception as error:
                st.error(f"Unexpected error: {error}")


elif menu == "Research":
    st.subheader("Generate Research Summary")

    st.info(
        f"Logged in as: {st.session_state.username} "
        f"| MongoDB User ID: {st.session_state.user_id}"
    )

    with st.form("research_form"):
        topic = st.text_area(
            "Research Topic",
            placeholder="Example: Artificial Intelligence in Healthcare",
            height=140
        )
        submit = st.form_submit_button("Generate Summary")

    if submit:
        if not topic.strip():
            st.warning("Please enter a topic.")

        elif len(topic.strip()) < 3:
            st.warning("Topic must be at least 3 characters.")

        else:
            with st.spinner("Research Agent is searching and summarizing..."):
                try:
                    response = requests.post(
                        f"{BASE_URL}/generate-summary",
                        json={
                            "user_id": st.session_state.user_id,
                            "topic": topic.strip()
                        },
                        headers={
                            "Authorization": f"Bearer {st.session_state.access_token}"
                        },
                        timeout=90
                    )

                    if response.status_code == 200:
                        data = response.json()

                        st.success("Summary generated successfully!")

                        st.subheader("📌 Topic")
                        st.write(topic.strip())

                        st.subheader("📝 Summary")
                        st.write(data["summary"])

                        st.subheader("⏱ Execution Time")
                        st.write(f"{data['execution_time']} seconds")

                        st.info("This result was saved into MongoDB Atlas research_logs collection.")

                    elif response.status_code == 401:
                        st.error("Session expired. Please login again.")
                        logout_user()
                        st.rerun()

                    else:
                        st.error("API Error")
                        st.code(response.text)

                except requests.exceptions.ConnectionError:
                    st.error("FastAPI server is not running.")
                    st.code("uvicorn app.main:app --reload")

                except requests.exceptions.Timeout:
                    st.error("Request timed out. Try again.")

                except Exception as error:
                    st.error(f"Unexpected error: {error}")


elif menu == "Logout":
    st.subheader("Logout")

    st.write(f"You are logged in as **{st.session_state.username}**.")

    if st.button("Logout"):
        logout_user()
        st.success("Logged out successfully.")
        st.rerun()