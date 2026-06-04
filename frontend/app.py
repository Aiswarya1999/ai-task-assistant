import streamlit as st
import requests

# 1. Title updated to "Secure AI Assistant" as requested
st.set_page_config(page_title="Secure AI Assistant", page_icon="🛡️", layout="wide")

BACKEND_URL = "http://localhost:8000"

st.title("🛡️ Secure AI Assistant")
st.markdown("---")

# -------------------------------------------------------------------
# SIDEBAR NAVIGATION & VIEWER
# -------------------------------------------------------------------
st.sidebar.header("📋 Task Management")

# Sidebar options: Task Creator vs. Views
menu = st.sidebar.radio("Navigate", ["Smart Task Creator", "Task Reminders", "Completed Tasks"])

# -------------------------------------------------------------------
# FEATURE 1: SMART TASK CREATOR
# -------------------------------------------------------------------
if menu == "Smart Task Creator":
    st.subheader("Type your note/reminder:")
    
    user_note = st.text_area(
        "Input text area:", 
        label_visibility="collapsed",
        placeholder="Example: Call Alice tomorrow at 10 AM regarding the deployment phase on cell +91 98765 43210."
    )
    
    # Button changed to "Save Task"
    if st.button("Save Task", use_container_width=True):
        if user_note.strip():
            with st.spinner("Processing local privacy filters..."):
                try:
                    payload = {"note": user_note}
                    task_res = requests.post(f"{BACKEND_URL}/tasks/auto", json=payload)
                    
                    if task_res.status_code == 200:
                        # Success indicator changed to "task saved!"
                        st.success("🎉 task saved!")
                        task_data = task_res.json()
                        
                        st.markdown("### 🖥️ Real-Time Pipeline Visualizer")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info("🔒 Zero-Trust Sanitized Text (Saved to DB):")
                            st.code(task_data.get("description", "Error fetching data."))
                        with col2:
                            st.success("🤖 Context-Aware AI Task Title:")
                            st.write(f"**{task_data.get('title', 'New Task')}**")
                    else:
                        st.error(f"Backend Issue: {task_res.status_code}")
                except Exception as e:
                    st.error(f"Could not connect to backend pipeline: {e}")
        else:
            st.warning("Please input a note first.")

# -------------------------------------------------------------------
# FEATURE 2: TASK REMINDERS (ACTIVE)
# -------------------------------------------------------------------
elif menu == "Task Reminders":
    st.header("⏳ Active Task Reminders")
    st.markdown("This section fetches active corporate action items from your encrypted data pipeline.")
    
    # Placeholder layout showcasing future database bindings
    st.info("Fetching your active, sanitized tasks from PostgreSQL database...")
    
    # Static mockup mimicking real database output items
    with st.expander("📌 Call Person (Pending)", expanded=True):
        st.code("call <PERSON> at <PHONE_NUMBER>")
        st.button("Mark Completed", key="btn_complete_1")

# -------------------------------------------------------------------
# FEATURE 3: COMPLETED TASKS
# -------------------------------------------------------------------
elif menu == "Completed Tasks":
    st.header("✅ Completed Task History")
    st.markdown("Review historical items that have been safely processed and cleared.")
    
    st.success("No pending validations. Archives secure.")
    st.text("✔️ Title: Review System Logs | Description: Checked production cluster for anomalies.")