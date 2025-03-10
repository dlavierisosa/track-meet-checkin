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
                        athlete_match = re.match(r"(.+)\s+([\w ]+)\s+(\d+\.?\d*m?|NH|ND|NT)", line)
                        if athlete_match and event_name:
                            extracted_data.append([
                                event_name,
                                athlete_match.group(1).strip(),  # Athlete Name
                                athlete_match.group(2).strip(),  # School Name
                                athlete_match.group(3).strip()   # Seed Mark
                            ])
    return extracted_data

# Streamlit UI
st.title("Track Meet Electronic Check-In")

uploaded_file = st.file_uploader("Upload Meet Entries PDF", type=["pdf"])

data = extract_data_from_pdf(uploaded_file) if uploaded_file else []

df = pd.DataFrame(data, columns=["Event", "Athlete", "School", "Seed Mark"])
df["Checked In"] = False

# Search Functionality
search_query = st.text_input("Search for an Athlete or Event")
if search_query:
    df = df[df.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]

# Display and Edit Table
edited_df = st.data_editor(df, key="checkin_table")

# Download Updated List
st.download_button(
    "Download Updated Check-In List",
    edited_df.to_csv(index=False).encode("utf-8"),
    "track_meet_checkin.csv",
    "text/csv",
    key="download-csv"
)
