import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from openai import OpenAI

# ================= CONFIG =================
st.set_page_config(page_title="Productivity AI Toolkit", layout="wide")
st.title(" Productivity AI Toolkit")
st.markdown("AI tools to evaluate ideas, reduce unnecessary meetings, and identify automation opportunities.")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ============ SESSION AI LIMIT ============
if "ai_calls" not in st.session_state:
    st.session_state.ai_calls = 0

MAX_CALLS = 5

def can_use_ai():
    if st.session_state.ai_calls >= MAX_CALLS:
        st.warning("⚠️ AI usage limit reached for this session. Please try again later.")
        return False
    st.session_state.ai_calls += 1
    return True

# ================= TABS =================
tabs = st.tabs(["💡 Idea Evaluator", "📅 Meeting Checker", "🔁 Work Automation Finder"])

#  IDEA EVALUATOR

with tabs[0]:
    st.header("💡 AI Idea Evaluator")

    col1, col2 = st.columns(2)

    with col1:
        idea_name = st.text_input("Idea / Project Name")
        problem = st.text_area("Problem it solves")
        users = st.text_input("Target Users")
        benefits = st.text_area("Expected Benefits")
        effort = st.selectbox("Estimated Effort", ["Low", "Medium", "High"])
        dependencies = st.text_area("Dependencies / Risks")

    if st.button("Evaluate Idea"):
        if can_use_ai():
            prompt = f"""
            Evaluate this business idea.

            Idea: {idea_name}
            Problem: {problem}
            Users: {users}
            Benefits: {benefits}
            Effort: {effort}
            Risks/Dependencies: {dependencies}

            Score from 1-10 for:
            - Business Impact
            - Clarity
            - Risk Level
            - Effort Level

            Then provide:
            1. Overall Recommendation (GO / REWORK / NOT WORTH IT)
            2. Short reasoning
            3. 2 improvement suggestions
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            result = response.choices[0].message.content

            with col2:
                st.subheader("📊 AI Evaluation")
                st.write(result)

#  MEETING CHECKER

with tabs[1]:
    st.header("📅 Meeting Necessity Checker")

    topic = st.text_input("Meeting Topic")
    objective = st.text_area("Meeting Objective")
    decisions = st.radio("Are decisions required?", ["Yes", "No"])
    attendees = st.number_input("Number of Attendees", 1, 50, 5)
    urgency = st.selectbox("Urgency Level", ["Low", "Medium", "High"])

    if st.button("Evaluate Meeting"):
        if can_use_ai():
            prompt = f"""
            Determine if this meeting is necessary.

            Topic: {topic}
            Objective: {objective}
            Decisions Needed: {decisions}
            Number of Attendees: {attendees}
            Urgency: {urgency}

            Provide:
            1. Verdict (Meeting Needed / Send Email Instead / Reduce Scope)
            2. Suggested Duration
            3. Suggested Attendee Roles
            4. Simple Agenda
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            st.subheader("🧠 AI Meeting Verdict")
            st.write(response.choices[0].message.content)

#  WORK AUTOMATION FINDER

with tabs[2]:
    st.header("🔁 Repetitive Work Identifier")

    st.write("List tasks you repeatedly do each week:")

    df = st.data_editor(pd.DataFrame({
        "Task": ["Updating weekly Excel report", "Copying data from emails"],
        "Hours per Week": [4, 3],
        "Tool Used": ["Excel", "Outlook"]
    }), num_rows="dynamic")

    if st.button("Analyze Workload"):
        df["Monthly Hours"] = df["Hours per Week"] * 4
        total_hours = df["Monthly Hours"].sum()

        st.subheader("⏳ Monthly Time Spent")
        st.bar_chart(df.set_index("Task")["Monthly Hours"])
        st.write(f"**Total Monthly Hours on Repetitive Work: {total_hours} hrs**")

        if can_use_ai():
            task_summary = df.to_string()

            prompt = f"""
            These are recurring work tasks:

            {task_summary}

            Identify:
            1. Which tasks can be automated
            2. Suggested tools (RPA, Python, Power Automate, Dashboards, etc.)
            3. Estimated difficulty (Easy/Medium/Hard)
            4. Potential time savings
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            st.subheader("🤖 AI Automation Opportunities")
            st.write(response.choices[0].message.content)

# ================= FOOTER =================
st.markdown("---")
st.caption("Built with Streamlit + OpenAI | MAS Productivity AI Toolkit")
