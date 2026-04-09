import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Mentoring System", layout="wide")

st.title("🎓 AI Powered Student Mentoring System")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.sidebar.file_uploader("Upload Student Dataset", type=["csv"])

if uploaded_file is not None:

    data = pd.read_csv(uploaded_file)

    st.subheader("📄 Raw Data")
    st.dataframe(data)

    # ---------------- SRI CALCULATION ----------------
    st.subheader("📊 Student Readiness Index")

    data["SRI"] = (
        0.30 * data["APS"] +
        0.25 * data["WWS"] +
        0.20 * data["PTMS"] +
        0.25 * data["CRS"]
    )

    # ---------------- STATUS (YOUR LOGIC) ----------------
    def colour(SRI):
        if SRI >= 80:
            return "Green"
        elif SRI >= 60:
            return "Blue"
        elif SRI >= 40:
            return "Yellow"
        else:
            return "Red"

    data["Status"] = data["SRI"].apply(colour)

    # ---------------- CLUSTERING ----------------
    st.subheader("🤖 Student Clustering")

    features = data[["APS", "WWS", "PTMS", "CRS"]]

    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=4, random_state=42)
    data["cluster"] = kmeans.fit_predict(scaled)

    # ---------------- CLUSTER INTERPRETATION ----------------
    cluster_labels = {}

    for cluster in data["cluster"].unique():

        avg_sri = data[data["cluster"] == cluster]["SRI"].mean()
        avg_crs = data[data["cluster"] == cluster]["CRS"].mean()
        avg_aps = data[data["cluster"] == cluster]["APS"].mean()

        if avg_sri < 55:
            cluster_labels[cluster] = "At-Risk Students"

        elif avg_aps > 75 and avg_crs > 70:
            cluster_labels[cluster] = "High Performers"

        elif avg_aps > 70 and avg_crs < 60:
            cluster_labels[cluster] = "Career-Confused Students"

        else:
            cluster_labels[cluster] = "Moderate / Improving Students"

    data["cluster_Type"] = data["cluster"].map(cluster_labels)

    # ---------------- FINAL TABLE ----------------
    st.subheader("🎯 Final Results")

    st.dataframe(
        data[["student_id", "APS", "WWS", "PTMS", "CRS", "SRI", "Status", "cluster", "cluster_Type"]]
    )

    # ---------------- METRICS ----------------
    st.subheader("📊 Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Students", len(data))
    col2.metric("Average SRI", round(data["SRI"].mean(), 2))
    col3.metric("High Risk (<55)", (data["SRI"] < 55).sum())

    # ---------------- CLUSTER CHART ----------------
    st.subheader("📊 Cluster Distribution")

    cluster_counts = data["cluster_Type"].value_counts()

    fig, ax = plt.subplots()
    ax.bar(cluster_counts.index, cluster_counts.values)
    plt.xticks(rotation=20)

    st.pyplot(fig)

    # ---------------- SRI HISTOGRAM ----------------
    st.subheader("📈 SRI Distribution")

    fig2, ax2 = plt.subplots()
    ax2.hist(data["SRI"], bins=10)

    st.pyplot(fig2)

    # ---------------- DOWNLOAD ----------------
    csv = data.to_csv(index=False).encode('utf-8')

    st.download_button(
        "Download Results",
        data=csv,
        file_name="mentoring_output.csv",
        mime="text/csv"
    )

else:
    st.info("Upload a dataset to start")