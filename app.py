import streamlit as st
import pandas as pd
import pdfplumber
import re

# Function to extract data from PDF with improved parsing logic
def extract_data_from_pdf(uploaded_file):
    extracted_data = []
    raw_text = ""  # Store raw text for debugging
    if uploaded_file is not None:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                raw_text += text + "\n\n"  # Collect raw text
                if text:
                    lines = text.split('\n')
                    event_name = ""
                    heat_number = 0
                    for line in lines:
                        line = line.strip()
                        
                        # Detect event headers (Improved Regex)
                        event_match = re.match(r"^Event\s+\d+\s+(.+)", line)
                        if event_match:
                            event_name = event_match.group(1).strip()
                            heat_number = 0  # Reset heat count for new events
                            continue
                        
                        # Detect heat number
                        heat_match = re.match(r"^(Section|Heat)\s+(\d+)\s+of", line)
                        if heat_match:
                            heat_number = int(heat_match.group(2))
                            continue
                        
                        # Extract athlete details properly
                        athlete_match = re.match(r"^([A-Za-z'\- ]+),\s+([A-Za-z'\- ]+)\s+(\d+:\d+\.\d+|\d+\.\d+m?|NH|ND|NT)\s+([A-Za-z'\- ]+)", line)
                        if athlete_match and event_name:
                            full_event_name = f"{event_name} - Heat {heat_number}" if heat_number > 0 else event_name
                            extracted_data.append([
                                full_event_name,
                                f"{athlete_match.group(2)} {athlete_match.group(1)}",  # Athlete Name (Corrected Order)
                                athlete_match.group(4),  # School Name
                                athlete_match.group(3)   # Seed Mark
                            ])
    return extracted_data, raw_text

# Streamlit UI
st.set_page_config(page_title="Track Meet Check-In", layout="wide")
st.title("🏃 Track Meet Electronic Check-In")
st.write("Upload a track meet entry PDF and efficiently manage athlete check-ins.")

uploaded_file = st.file_uploader("📂 Upload Meet Entries PDF", type=["pdf"])

data, raw_text = extract_data_from_pdf(uploaded_file) if uploaded_file else ([], "")
df = pd.DataFrame(data, columns=["Event", "Athlete", "School", "Seed Mark"])
df["Checked In"] = False

# Debugging: Show extracted raw text
if uploaded_file:
    st.subheader("📜 Extracted Raw Text (Debugging)")
    st.text_area("Raw text from PDF", raw_text, height=200)

if not df.empty:
    # Ensure heats appear in correct order
    df.sort_values(by=["Event", "Seed Mark"], ascending=[True, True], inplace=True, na_position='last')
    
    # Search Bar
    search_query = st.text_input("🔍 Search for an Event, Athlete, or Heat")
    if search_query:
        df = df[df.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]
    
    # Select Event
    unique_events = df["Event"].unique().tolist()
    selected_event = st.selectbox("🏅 Select an Event", ["Select an event"] + unique_events)
    
    if selected_event != "Select an event":
        # Filter DataFrame by selected event
        filtered_df = df[df["Event"] == selected_event]
        
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
    st.warning("⚠️ No data was extracted. Please check if the PDF is formatted correctly.")




