import streamlit as st
import pandas as pd
import pdfplumber
import re

# Function to extract data from PDF
def extract_data_from_pdf(uploaded_file):
    extracted_data = []
    if uploaded_file is not None:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    lines = text.split('\n')
                    event_name = ""
                    for line in lines:
                        # Detect event headers
                        event_match = re.match(r"Event\s+\d+\s+(.*)", line)
                        if event_match:
                            event_name = event_match.group(1).strip()
                        
                        # Extract athlete details
                        athlete_match = re.match(r"(.+?)\s+([\w ]+)\s+((?:\d+\.\d+m?)|NH|ND|NT|\d+:\d+\.\d+)", line)
                        if athlete_match and event_name:
                            extracted_data.append([
                                event_name,
                                athlete_match.group(1).strip(),  # Athlete Name
                                athlete_match.group(2).strip(),  # School Name
                                athlete_match.group(3).strip()   # Seed Mark
                            ])
    return extracted_data

# Streamlit UI
st.title("🏃 Track Meet Electronic Check-In")
st.write("Upload a track meet entry PDF and easily manage athlete check-ins.")

uploaded_file = st.file_uploader("📂 Upload Meet Entries PDF", type=["pdf"])

data = extract_data_from_pdf(uploaded_file) if uploaded_file else []
df = pd.DataFrame(data, columns=["Event", "Athlete", "School", "Seed Mark"])
df["Checked In"] = False

if not df.empty:
    # Select Event
    unique_events = df["Event"].unique().tolist()
    selected_event = st.selectbox("🏅 Select an Event", ["Select an event"] + unique_events)
    
    if selected_event != "Select an event":
        # Filter DataFrame by selected event and sort by Seed Mark
        filtered_df = df[df["Event"] == selected_event].sort_values(by=["Seed Mark"], ascending=True, na_position='last')
        
        # Display Check-in Table
        edited_df = st.data_editor(filtered_df, key="checkin_table", column_config={
            "Checked In": st.column_config.CheckboxColumn("Check-In")
        })
        
        # Download Updated List
        st.download_button(
            "📥 Download Updated Check-In List",
            edited_df.to_csv(index=False).encode("utf-8"),
            "track_meet_checkin.csv",
            "text/csv",
            key="download-csv"
        )
else:
    st.info("Upload a PDF to begin.")


