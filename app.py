import fitz  # PyMuPDF
import pandas as pd
import datetime as dt
import re
import streamlit as st
from io import StringIO

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text

# Function to clean and normalize text
def clean_extracted_text(text):
    text_lines = text.splitlines()
    unique_lines = []
    
    for line in text_lines:
        if line.strip() and line not in unique_lines:
            unique_lines.append(line)
    
    clean_text = "\n".join(unique_lines)
    clean_text = re.sub(r"Credits.*|Teaching Scheme.*|Lab:.*|Tut:.*", "", clean_text)
    clean_text = re.sub(r"Course Relevance:.*|SECTION \d.*|SY-TY.*|Vishwakarma.*|Issue.*", "", clean_text)
    clean_text = re.sub(r"(Routing Protocols.*?QoS.\s*\(6 Hours\)\s*)+", 
                        "Routing Protocols- Distance Vector, Link State, RIP, OSPF, BGP, Congestion control and QoS. (6 Hours)\n", clean_text)
    clean_text = re.sub(r"\n\s*\n", "\n", clean_text).strip()
    return clean_text

# Function to extract topics for a specific subject
def extract_topics_for_subject(pdf_text, subject_name):
    subject_pattern = re.compile(rf"\b{subject_name}\b", re.IGNORECASE)
    start_pattern = re.compile(r"\b(SECTION \d.*)\b", re.IGNORECASE)
    end_pattern = re.compile(r"\b(List of Tutorials|List of Practical’s|Course Outcomes)\b", re.IGNORECASE)

    match_subject = subject_pattern.search(pdf_text)
    if not match_subject:
        return f"Subject '{subject_name}' not found in the PDF."
    
    start_pos = match_subject.end()
    match_start = start_pattern.search(pdf_text, start_pos)
    if not match_start:
        return f"Topics for '{subject_name}' not found."
    
    match_end = end_pattern.search(pdf_text, match_start.end())
    if match_end:
        topics_text = pdf_text[match_start.end():match_end.start()].strip()
    else:
        topics_text = pdf_text[match_start.end():].strip()

    cleaned_topics = clean_extracted_text(topics_text)
    unique_topics = set()
    final_topics = []

    for line in cleaned_topics.splitlines():
        stripped_line = line.strip()
        if stripped_line and stripped_line not in unique_topics:
            unique_topics.add(stripped_line)
            final_topics.append(stripped_line)

    return final_topics  # Return a list of topics

# Function to extract public holidays from the academic calendar
def extract_public_holidays(academic_calendar_text):
    date_pattern = r"\b\d{2}/\d{2}/\d{4}\b"
    holidays = re.findall(date_pattern, academic_calendar_text)
    holiday_dates = [dt.datetime.strptime(date, "%d/%m/%Y").date() for date in holidays]
    return set(holiday_dates)

# Function to generate the lecture schedule
def generate_schedule(start_date, end_date, lecture_days, public_holidays, topics):
    current_date = start_date
    lecture_no = 1
    schedule = []
    
    while current_date <= end_date and lecture_no <= len(topics):
        if current_date.weekday() in lecture_days and current_date not in public_holidays:
            # Get the corresponding topic for the lecture
            topic = topics[lecture_no - 1]
            schedule.append({
                "Date": current_date,
                "Day": current_date.strftime("%A"),
                "Lecture No": lecture_no,
                "Topic": topic
            })
            lecture_no += 1
        current_date += dt.timedelta(days=1)
    
    # Convert the schedule to a DataFrame
    df_schedule = pd.DataFrame(schedule)
    return df_schedule

# Streamlit App
def main():
    st.title("Lecture Schedule Generator")
    
    # File upload section for syllabus and academic calendar
    syllabus_file = st.file_uploader("Upload Syllabus PDF", type="pdf")
    academic_calendar_file = st.file_uploader("Upload Academic Calendar PDF", type="pdf")
    
    subject_name = st.text_input("Enter the subject name")

    if syllabus_file and academic_calendar_file and subject_name:
        syllabus_pdf_text = extract_text_from_pdf(syllabus_file)
        academic_calendar_text = extract_text_from_pdf(academic_calendar_file)
        
        topics = extract_topics_for_subject(syllabus_pdf_text, subject_name)
        
        if isinstance(topics, str):  # If an error message is returned
            st.error(topics)
        else:
            st.success(f"Topics for {subject_name} extracted successfully.")
            st.write("**Topics:**")
            st.write(topics)

            # Get start and end dates
            start_date_str = st.date_input("Enter the semester start date")
            end_date_str = st.date_input("Enter the semester end date")

            # Get lecture days
            lecture_days_input = st.text_input("Enter the lecture days (e.g., 0 for Monday, 2 for Wednesday, 4 for Friday)", value="0,2,4")
            lecture_days = [int(day.strip()) for day in lecture_days_input.split(",")]

            # Extract public holidays from academic calendar
            public_holidays = extract_public_holidays(academic_calendar_text)

            if st.button("Generate Schedule"):
                # Generate the lecture schedule
                lecture_schedule = generate_schedule(start_date_str, end_date_str, lecture_days, public_holidays, topics)
                st.write("**Lecture Schedule:**")
                st.dataframe(lecture_schedule)

                # Download option for the schedule
                csv = lecture_schedule.to_csv(index=False)
                st.download_button("Download Schedule as CSV", data=csv, file_name="lecture_schedule.csv", mime="text/csv")

if __name__ == "__main__":
    main()
