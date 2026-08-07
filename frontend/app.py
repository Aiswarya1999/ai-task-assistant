import streamlit as st
import requests


def main():
    st.title("Task Dashboard")
    with st.form(key="task_form"):
        task_description = st.text_area(
            "Task Description", placeholder="Enter task description"
        )
        submitted = st.form_submit_button("Create Task")
    if submitted:
        try:
            response = requests.post(
                "http://localhost:8000/tasks/auto", json={"note": task_description}
            )
            response.raise_for_status()
            task = response.json()
            st.write(task)
        except requests.exceptions.HTTPError as errh:
            st.error(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            st.error(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            st.error(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            st.error(f"Something went wrong: {err}")


if __name__ == "__main__":
    main()