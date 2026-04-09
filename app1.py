import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Mentoring System", page_icon="🎓", layout="wide")

st.title("🎓 AI Powered Student Mentoring System")

uploaded_file = st.sidebar.file_uploader("Upload Student CSV", type=["csv"])

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.subheader("📄 Raw Data")
    st.dataframe(df)

    # ---------------- APS ----------------
    # Academic Performance Score
    df["APS"] = (
        (df["gpa"] / 10) * 100 +
        df["attendance"] +
        df["assignments_completion"]
    ) / 3

    # ---------------- WWS ----------------
    # Wellness Score
    df["WWS"] = (
        (10 - df["stress_level"]) * 10 +   # less stress = good
        (df["sleep_hours"] / 8) * 100 +
        (df["mental_wellbeing"] * 10)
    ) / 3

    # ---------------- PTMS ----------------
    # Productivity Score
    df["PTMS"] = (
        (df["productivity_score"] * 10) +
        ((10 - df["distractions"]) * 10)
    ) / 2

    # ---------------- CRS ----------------
    # Career Readiness Score
    df["CRS"] = (
        (df["career_clarity"] * 10) +
        (df["skill_readiness"] * 10) +
        df["engagement_score"]
    ) / 3

    st.subheader("📊 Calculated Scores")
    st.dataframe(df[["APS", "WWS", "PTMS", "CRS"]])

    # ---------------- SRI ----------------
    df["SRI"] = (
        0.30 * df["APS"] +
        0.25 * df["WWS"] +
        0.20 * df["PTMS"] +
        0.25 * df["CRS"]
    )

    # ---------------- RISK ----------------
    def risk(score):
        if score < 50:
            return "High Risk"
        elif score < 70:
            return "Moderate Risk"
        else:
            return "Low Risk"

    df["Risk_Level"] = df["SRI"].apply(risk)

    # ---------------- MENTOR ----------------
    # ---------------- LOAD MENTORS ----------------
mentors = pd.read_csv("mentors.csv")

# ---------------- MAP NEED ----------------
def get_need(risk):
    if risk == "High Risk":
        return "Academic"
    elif risk == "Moderate Risk":
        return "Skill"
    else:
        return "Career"

df["Need"] = df["Risk_Level"].apply(get_need)

# ---------------- MATCH MENTOR ----------------
# ---------------- LOAD MENTORS ----------------
mentors = pd.read_csv("mentors.csv")

# ---------------- MAP NEED ----------------
def get_need(risk):
    if risk == "High Risk":
        return "Academic"
    elif risk == "Moderate Risk":
        return "Skill"
    else:
        return "Career"

df["Need"] = df["Risk_Level"].apply(get_need)

# ---------------- MATCH MENTOR ----------------
def match_mentor(need):
    eligible = mentors[mentors["expertise"] == need].copy()

    # filter available mentors
    eligible = eligible[eligible["current_students"] < eligible["max_students"]]

    if len(eligible) == 0:
        return "No Mentor Available"

    # pick least busy mentor
    best = eligible.sort_values("current_students").iloc[0]

    return best["mentor_name"]

df["Assigned_Mentor"] = df["Need"].apply(match_mentor)

    # ---------------- INTERVENTION ----------------
    interventions = {
        "High Risk": "Weekly mentoring + academic support",
        "Moderate Risk": "Skill development sessions",
        "Low Risk": "Career guidance"
    }

    df["Intervention"] = df["Risk_Level"].map(interventions)

    # ---------------- OUTPUT ----------------
    st.subheader("🎯 Final Results")
    st.dataframe(df)

    # ---------------- METRICS ----------------
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Students", len(df))
    col2.metric("Avg SRI", round(df["SRI"].mean(), 2))
    col3.metric("High Risk", (df["Risk_Level"] == "High Risk").sum())

    # ---------------- CHART ----------------
    st.subheader("📊 Risk Distribution")

    fig, ax = plt.subplots()
    df["Risk_Level"].value_counts().plot(kind="bar", ax=ax)

    st.pyplot(fig)

    # ---------------- DOWNLOAD ----------------
    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "Download Report",
        data=csv,
        file_name="final_report.csv",
        mime="text/csv"
    )

else:
    st.info("Upload dataset to start")
