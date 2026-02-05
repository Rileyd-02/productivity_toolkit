import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from openai import OpenAI
from datetime import datetime

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Productivity AI Toolkit", layout="wide")
st.title("🚀 Productivity AI Toolkit")
st.markdown("AI tools to evaluate ideas, reduce unnecessary meetings, and identify automation opportunities.")

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

# ============ SESSION AI LIMIT ============
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
        messages=[{"role": "system", "content": f"You are a senior corporate productivity consultant helping a {user_role} improve efficiency."},
                  {"role": "user", "content": prompt}],
        extra_headers={
            "HTTP-Referer": "https://your-app-name.streamlit.app",
            "X-Title": "Corporate Productivity Toolkit"
        }
    )
    return response.choices[0].message.content

def save_history(entry):
    st.session_state.history.append(entry)

# ================= TABS =================
tabs = st.tabs(["💡 Idea Evaluator", "📅 Meeting Checker", "🔁 Work Automation Finder", "📊 Productivity Dashboard"])

# ================= IDEA EVALUATOR =================
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
Evaluate this internal business idea and provide structured analysis.

Idea: {idea_name}
Problem: {problem}
Users: {users}
Benefits: {benefits}
Effort: {effort}
Risks: {dependencies}

Provide:
1. Scores (1-10): Impact, Clarity, Risk, Effort
2. Overall Recommendation
3. Reasoning
4. Two improvement suggestions
"""
            result = ask_ai(prompt)

            with col2:
                st.subheader("📊 AI Evaluation")
                st.write(result)

                report = f"Idea Evaluation Report\n\n{result}"
                st.download_button("⬇ Download Report", report, file_name="idea_evaluation.txt")

                save_history({"type": "Idea", "name": idea_name, "result": result, "time": datetime.now()})

# ================= MEETING CHECKER =================
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

Provide verdict, duration, roles, and agenda.
"""
            result = ask_ai(prompt)
            st.subheader("🧠 AI Meeting Verdict")
            st.write(result)

            minutes_prompt = f"Create professional meeting minutes template for: {topic}"
            minutes = ask_ai(minutes_prompt)

            st.download_button("⬇ Download Meeting Minutes Template", minutes, file_name="meeting_minutes.txt")

            save_history({"type": "Meeting", "name": topic, "result": result, "time": datetime.now()})

# ================= WORK AUTOMATION FINDER =================
with tabs[2]:
    st.header("🔁 Repetitive Work Identifier")

    df = st.data_editor(pd.DataFrame({
        "Task": ["Updating weekly Excel report", "Copying data from emails"],
        "Hours per Week": [4, 3],
        "Tool Used": ["Excel", "Outlook"]
    }), num_rows="dynamic")

    if st.button("Analyze Workload"):
        df["Monthly Hours"] = df["Hours per Week"] * 4
        total_hours = df["Monthly Hours"].sum()

        st.bar_chart(df.set_index("Task")["Monthly Hours"])
        st.write(f"**Total Monthly Hours: {total_hours} hrs**")

        if total_hours > 40:
            st.warning("⚠️ High repetitive workload detected. Automation recommended!")

        if can_use_ai():
            result = ask_ai(f"Suggest automation solutions for:\n{df.to_string()}")
            st.subheader("🤖 AI Automation Opportunities")
            st.write(result)

            st.info("💡 Common Tools: Power Automate | Python Scripts | RPA | Power BI Dashboards")

            save_history({"type": "Automation", "name": "Work Tasks", "result": result, "time": datetime.now(), "hours": total_hours})

# ================= DASHBOARD =================
with tabs[3]:
    st.header("📊 Productivity Insights Dashboard")

    if st.session_state.history:
        hist_df = pd.DataFrame(st.session_state.history)

        st.metric("Total Evaluations", len(hist_df))
        st.metric("Ideas Reviewed", len(hist_df[hist_df["type"] == "Idea"]))
        st.metric("Meetings Checked", len(hist_df[hist_df["type"] == "Meeting"]))

        auto_hours = hist_df[hist_df["type"] == "Automation"]["hours"].sum() if "hours" in hist_df else 0
        st.metric("Repetitive Hours Identified", f"{auto_hours} hrs/month")

        fig = go.Figure(go.Bar(
            x=hist_df["type"].value_counts().index,
            y=hist_df["type"].value_counts().values
        ))
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No activity yet. Start using the tools to see insights!")

# ================= FOOTER =================
st.markdown("---")
st.caption("Powered by Digitalization@Intimates | MAS Productivity AI Toolkit")
