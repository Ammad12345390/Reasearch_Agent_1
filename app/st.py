import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/generate-summary"

st.set_page_config(
    page_title="Research Agent",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Research Agent")
st.write("Enter a topic and let the AI agent research and summarize it.")

with st.form("research_form"):
    user_id = st.text_input("User ID", placeholder="Example: user123")
    topic = st.text_area("Research Topic", placeholder="Example: Artificial Intelligence in Healthcare")

    submit = st.form_submit_button("Generate Summary")

if submit:
    if not user_id or not topic:
        st.warning("Please enter both User ID and Topic.")
    else:
        with st.spinner("Research Agent is working..."):
            try:
                response = requests.post(
                    API_URL,
                    json={
                        "user_id": user_id,
                        "topic": topic
                    }
                )

                if response.status_code == 200:
                    data = response.json()

                    st.success("Summary generated successfully!")

                    st.subheader("📌 Summary")
                    st.write(data["summary"])

                    st.subheader("⏱ Execution Time")
                    st.write(f"{data['execution_time']} seconds")

                else:
                    st.error("API Error")
                    st.write(response.text)

            except requests.exceptions.ConnectionError:
                st.error("FastAPI server is not running.")
                st.code("uvicorn app.main:app --reload")