import fitz  # PyMuPDF
import pandas as pd
import datetime as dt
import re

# pd.set_option('display.max_colwidth', None)  # No truncation of column width

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

# Function to save topics to a text file
def save_topics_to_file(topics, file_name="extracted_topics.txt"):
    with open(file_name, "w") as file:
        for topic in topics:
            file.write(f"{topic}\n")
    print(f"Topics successfully saved to {file_name}")

# Function to load topics from a text file
def load_topics_from_file(file_name="extracted_topics.txt"):
    topics = []
    with open(file_name, "r") as file:
        topics = [line.strip() for line in file.readlines()]
    return topics

# Function to extract public holidays from the academic calendar
def extract_public_holidays(academic_calendar_path):
    calendar_text = extract_text_from_pdf(academic_calendar_path)
    date_pattern = r"\b\d{2}/\d{2}/\d{4}\b"
    holidays = re.findall(date_pattern, calendar_text)
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

# Main function to handle the schedule generation
def create_lecture_schedule(start_date_str, end_date_str, lecture_days, academic_calendar_path, topics_file):
    start_date = dt.datetime.strptime(start_date_str, "%d/%m/%Y").date()
    end_date = dt.datetime.strptime(end_date_str, "%d/%m/%Y").date()

    # Extract public holidays from the uploaded academic calendar
    public_holidays = extract_public_holidays(academic_calendar_path)
    
    # Load topics from file (already extracted)
    topics = load_topics_from_file(topics_file)
    
    # Generate the schedule
    lecture_schedule = generate_schedule(start_date, end_date, lecture_days, public_holidays, topics)
    return lecture_schedule

# Function to run the entire process
def main():
    # Get user input for the subject name and PDF paths
    subject_name = input("Enter the subject name: ")
    pdf_path = "SYLLABUS.pdf"  # Replace with the path to your syllabus PDF
    topics_file = "extracted_topics.txt"  # Path to save extracted topics
    academic_calendar_path = "Academic_calendar_2024-25_sem1.pdf"  # Path to your academic calendar PDF

    # Extract topics for the specified subject
    pdf_text = extract_text_from_pdf(pdf_path)
    topics = extract_topics_for_subject(pdf_text, subject_name)

    if isinstance(topics, str):  # If an error message is returned
        print(topics)
    else:
        save_topics_to_file(topics)

        # Get start and end date of the semester from user
        start_date_str = input("Enter the semester start date (DD/MM/YYYY): ")
        end_date_str = input("Enter the semester end date (DD/MM/YYYY): ")

        # Get lecture days from user input
        lecture_days_input = input("Enter the lecture days (e.g., 0 for Monday, 2 for Wednesday, 4 for Friday, separated by commas): ")
        lecture_days = [int(day.strip()) for day in lecture_days_input.split(",")]

        # Generate the lecture schedule using the pre-extracted topics
        lecture_schedule = create_lecture_schedule(start_date_str, end_date_str, lecture_days, academic_calendar_path, topics_file)
        print("\nLecture Schedule:\n", lecture_schedule)

# Run the main function
if __name__ == "__main__":
    main()
