import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from openai import OpenAI
from datetime import datetime

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Productivity AI Toolkit", layout="wide")
st.title("🚀 Productivity AI Toolkit")
st.markdown("AI tools to identify automation opportunities, evaluate ideas, and reduce unnecessary meetings.")

# ================= USER ROLE =================
user_role = st.selectbox("Your Role", ["Operations", "Manager", "HR", "Finance", "IT"])

# ================= OPENROUTER CLIENT =================
if "OPENROUTER_API_KEY" not in st.secrets:
    st.error("❌ OPENROUTER_API_KEY not found in Streamlit secrets.")
    st.stop()

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "openai/gpt-4o-mini"

# ================= SESSION STATE =================
if "ai_calls" not in st.session_state:
    st.session_state.ai_calls = 0

if "history" not in st.session_state:
    st.session_state.history = []

MAX_CALLS = 8

def can_use_ai():
    if st.session_state.ai_calls >= MAX_CALLS:
        st.warning("⚠️ AI usage limit reached for this session.")
        return False
    st.session_state.ai_calls += 1
    return True

def ask_ai(prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"You are a corporate productivity consultant helping a {user_role} improve efficiency."},
            {"role": "user", "content": prompt}
        ],
        extra_headers={
            "HTTP-Referer": "https://your-app-name.streamlit.app",
            "X-Title": "Corporate Productivity Toolkit"
        }
    )
    return response.choices[0].message.content

def save_history(entry):
    # Ensure all records have same keys to prevent dashboard errors
    default_entry = {
        "type": "",
        "name": "",
        "result": "",
        "time": datetime.now(),
        "hours": 0,
        "savings": 0
    }
    default_entry.update(entry)
    st.session_state.history.append(default_entry)

# ================= TABS =================
tabs = st.tabs([
    "🔁 Work Automation Finder",
    "💡 Idea Evaluator",
    "📅 Meeting Checker",
    "📊 Productivity Dashboard"
])

# =====================================================
# 🔁 WORK AUTOMATION FINDER + ROI
# =====================================================
with tabs[0]:
    st.header("🔁 Repetitive Work & Automation ROI Calculator")

    df = st.data_editor(pd.DataFrame({
        "Task": ["Updating weekly Excel report", "Copying data from emails"],
        "Hours per Week": [4, 3],
        "Tool Used": ["Excel", "Outlook"]
    }), num_rows="dynamic")

    col1, col2 = st.columns(2)
    with col1:
        hourly_rate = st.number_input("Average Employee Hourly Cost ($)", 5, 200, 25)
    with col2:
        automation_cost = st.number_input("Estimated Automation Build Cost ($)", 0, 50000, 2000)

    if st.button("Analyze Automation Potential"):
        df["Monthly Hours"] = df["Hours per Week"] * 4
        total_hours = df["Monthly Hours"].sum()
        annual_hours = total_hours * 12

        annual_savings = annual_hours * hourly_rate
        roi = ((annual_savings - automation_cost) / automation_cost) * 100 if automation_cost else 0

        st.subheader("⏳ Time Spent on Repetitive Work")
        st.bar_chart(df.set_index("Task")["Monthly Hours"])

        st.metric("Monthly Hours Lost", f"{total_hours:.1f} hrs")
        st.metric("Annual Hours Lost", f"{annual_hours:.1f} hrs")
        st.metric("Potential Annual Savings", f"${annual_savings:,.0f}")
        st.metric("Estimated ROI", f"{roi:.1f}%")

        if total_hours > 40:
            st.warning("⚠️ Significant automation opportunity detected!")

        if can_use_ai():
            result = ask_ai(f"""
These recurring tasks were identified:

{df.to_string()}

Suggest:
1. Tasks suitable for automation
2. Tools to automate them
3. Difficulty level
4. Estimated % time reduction
""")
            st.subheader("🤖 AI Automation Plan")
            st.write(result)

            save_history({
                "type": "Automation",
                "name": "Task Analysis",
                "result": result,
                "hours": total_hours,
                "savings": annual_savings
            })

# =====================================================
# 💡 IDEA EVALUATOR
# =====================================================
with tabs[1]:
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
Evaluate this internal idea.

Idea: {idea_name}
Problem: {problem}
Users: {users}
Benefits: {benefits}
Effort: {effort}
Risks: {dependencies}
"""
            result = ask_ai(prompt)
            with col2:
                st.write(result)

            save_history({
                "type": "Idea",
                "name": idea_name,
                "result": result
            })

# =====================================================
# 📅 MEETING CHECKER
# =====================================================
with tabs[2]:
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
"""
            result = ask_ai(prompt)
            st.write(result)

            save_history({
                "type": "Meeting",
                "name": topic,
                "result": result
            })

# =====================================================
# 📊 PRODUCTIVITY DASHBOARD (FIXED)
# =====================================================
with tabs[3]:
    st.header("📊 Productivity Impact Dashboard")

    if st.session_state.history:
        hist_df = pd.DataFrame(st.session_state.history)

        st.metric("Total Evaluations", len(hist_df))
        st.metric("Ideas Reviewed", len(hist_df[hist_df["type"] == "Idea"]))
        st.metric("Meetings Checked", len(hist_df[hist_df["type"] == "Meeting"]))

        auto_hours = hist_df.loc[hist_df["type"] == "Automation", "hours"].sum()
        auto_savings = hist_df.loc[hist_df["type"] == "Automation", "savings"].sum()

        st.metric("Repetitive Hours Identified", f"{auto_hours:.1f} hrs/month")
        st.metric("Total Annual Savings Identified", f"${auto_savings:,.0f}")

        fig = go.Figure(go.Bar(
            x=hist_df["type"].value_counts().index,
            y=hist_df["type"].value_counts().values
        ))
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No activity yet. Run an analysis to see productivity insights!")

# ================= FOOTER =================
st.markdown("---")
st.caption("Powered by Digitalization@Intimates | MAS Productivity AI Toolkit")
