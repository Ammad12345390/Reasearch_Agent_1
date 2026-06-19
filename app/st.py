import streamlit as st
import requests
from streamlit_cookies_manager import EncryptedCookieManager

BASE_URL = "https://reasearch-agent-1-2.onrender.com"
#BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Research Agent",
    page_icon="🤖",
    layout="centered"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg,
        #0E1A35,
        #1877F2,
        #42A5F5
    );
}
.main-card {
    background: rgba(255,255,255,0.12);
    padding: 30px;
    border-radius: 22px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.25);
    backdrop-filter: blur(12px);
    margin-top: 20px;
}

.hero-title {
    text-align: center;
    font-size: 46px;
    font-weight: 800;
    color: white;
    margin-bottom: 5px;
}

.hero-subtitle {
    text-align: center;
    font-size: 18px;
    color: #d7f9ff;
    margin-bottom: 25px;
}

.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(90deg, #0077ff, #00d4ff);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 22px;
    font-weight: 700;
    width: 100%;
    transition: 0.3s;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    transform: scale(1.03);
    box-shadow: 0 0 18px #00d4ff;
    color: white;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #001f54, #003f88);
}

[data-testid="stSidebar"] * {
    color: white;
}

input, textarea {
    border-radius: 10px !important;
}

.success-box {
    background: rgba(0, 255, 180, 0.15);
    padding: 15px;
    border-radius: 14px;
    border-left: 5px solid #00ffc8;
}

.info-box {
    background: rgba(255,255,255,0.15);
    padding: 14px;
    border-radius: 14px;
    border-left: 5px solid #00d4ff;
}
</style>
""", unsafe_allow_html=True)

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
    "access_token": None,
    "page": "Login",
    "logout_clicked": False
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

if cookies.get("access_token") and not st.session_state.logout_clicked:
    st.session_state.logged_in = True
    st.session_state.user_id = cookies.get("user_id")
    st.session_state.username = cookies.get("username")
    st.session_state.email = cookies.get("email")
    st.session_state.access_token = cookies.get("access_token")
    st.session_state.page = "Research"

def save_login_to_cookie(data):
    st.session_state.logout_clicked = False
    cookies["access_token"] = data["access_token"]
    cookies["user_id"] = data["user_id"]
    cookies["username"] = data["username"]
    cookies["email"] = data["email"]
    cookies.save()

def logout_user():
    st.session_state.logout_clicked = True
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.email = None
    st.session_state.access_token = None
    st.session_state.page = "Login"

    cookies.pop("access_token", None)
    cookies.pop("user_id", None)
    cookies.pop("username", None)
    cookies.pop("email", None)
    cookies.save()

# ---------------- HEADER ----------------
st.markdown("""
<div class="hero-title">🤖 Research Agent</div>
<div class="hero-subtitle">
FastAPI + LangGraph + Tavily + Groq + MongoDB Atlas
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    menu = st.sidebar.radio(
        "Menu",
        ["Research", "Logout"],
        index=["Research", "Logout"].index(st.session_state.page)
        if st.session_state.page in ["Research", "Logout"] else 0
    )
else:
    menu = st.sidebar.radio(
        "Menu",
        ["Login", "Sign Up"],
        index=["Login", "Sign Up"].index(st.session_state.page)
        if st.session_state.page in ["Login", "Sign Up"] else 0
    )

st.session_state.page = menu

# ---------------- SIGN UP ----------------
if menu == "Sign Up":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
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
                    st.session_state.page = "Login"
                    st.rerun()
                else:
                    st.error("Sign up failed.")
                    st.code(response.text)

            except requests.exceptions.ConnectionError:
                st.error("FastAPI server is not running.")
                st.code("uvicorn app.main:app --reload")
            except Exception as error:
                st.error(f"Unexpected error: {error}")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- LOGIN ----------------
elif menu == "Login":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
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
                    st.session_state.page = "Research"

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

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- RESEARCH ----------------
elif menu == "Research":
    if not st.session_state.logged_in:
        st.warning("Please login first.")
        st.session_state.page = "Login"
        st.rerun()

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Generate Research Summary")

    st.markdown(f"""
    <div class="info-box">
        Logged in as: <b>{st.session_state.username}</b><br>
        MongoDB User ID: <b>{st.session_state.user_id}</b>
    </div>
    """, unsafe_allow_html=True)

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

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- LOGOUT ----------------
elif menu == "Logout":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Logout")

    st.write(f"You are logged in as **{st.session_state.username}**.")

    if st.button("Logout"):
        logout_user()
        st.success("Logged out successfully.")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
