import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from openai import OpenAI

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Productivity AI Toolkit", layout="wide")
st.title(" Productivity AI Toolkit")
st.markdown("AI tools to evaluate ideas, reduce unnecessary meetings, and identify automation opportunities.")

# ================= OPENROUTER CLIENT =================
if "OPENROUTER_API_KEY" not in st.secrets:
    st.error("❌ OPENROUTER_API_KEY not found in Streamlit secrets.")
    st.stop()

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "openai/gpt-4o-mini"

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

def ask_ai(prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        extra_headers={
            "HTTP-Referer": "https://your-app-name.streamlit.app",
            "X-Title": "Corporate Productivity Toolkit"
        }
    )
    return response.choices[0].message.content

# ================= TABS =================
tabs = st.tabs(["💡 Idea Evaluator", "📅 Meeting Checker", "🔁 Work Automation Finder"])

# IDEA EVALUATOR

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
Evaluate this business idea:

Idea: {idea_name}
Problem: {problem}
Users: {users}
Benefits: {benefits}
Effort: {effort}
Risks: {dependencies}

Provide:
1. Scores (1-10) for Impact, Clarity, Risk, Effort
2. Overall Recommendation (GO / REWORK / NOT WORTH IT)
3. Reasoning
4. Two improvement suggestions
"""
            result = ask_ai(prompt)
            with col2:
                st.subheader("📊 AI Evaluation")
                st.write(result)

# MEETING CHECKER

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
Should this meeting happen?

Topic: {topic}
Objective: {objective}
Decisions Needed: {decisions}
Attendees: {attendees}
Urgency: {urgency}

Provide:
1. Verdict (Meeting Needed / Send Email Instead / Reduce Scope)
2. Suggested Duration
3. Suggested Attendee Roles
4. Simple Agenda
"""
            result = ask_ai(prompt)
            st.subheader("🧠 AI Meeting Verdict")
            st.write(result)

#  WORK AUTOMATION FINDER

with tabs[2]:
    st.header("🔁 Repetitive Work Identifier")
    st.write("List recurring tasks you perform each week:")

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
1. Tasks suitable for automation
2. Suggested tools (RPA, Python, Power Automate, dashboards, etc.)
3. Automation difficulty (Easy/Medium/Hard)
4. Potential monthly time savings
"""
            result = ask_ai(prompt)
            st.subheader("🤖 AI Automation Opportunities")
            st.write(result)

# ================= FOOTER =================
st.markdown("---")
st.caption("Powered by Digitalization@Intimates | MAS Productivity AI Toolkit")
