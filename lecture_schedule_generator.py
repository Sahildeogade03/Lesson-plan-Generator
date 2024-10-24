import fitz  # PyMuPDF
import pandas as pd
import datetime as dt
import re

# Function to extract text from PDF (for public holidays)
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text

# Function to extract public holidays from the academic calendar
def extract_public_holidays(academic_calendar_path):
    calendar_text = extract_text_from_pdf(academic_calendar_path)
    date_pattern = r"\b\d{2}/\d{2}/\d{4}\b"
    holidays = re.findall(date_pattern, calendar_text)
    holiday_dates = [dt.datetime.strptime(date, "%d/%m/%Y").date() for date in holidays]
    return set(holiday_dates)

# Function to load topics from a text file
def load_topics_from_file(file_path):
    topics = []
    with open(file_path, "r") as file:
        topics = [line.strip() for line in file.readlines()]
    return topics

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

# Example usage
if __name__ == "__main__":
    # Load topics from the pre-extracted topics file
    topics_file = "organized_lectures.txt"  # Replace with the correct path to the extracted topics file

    # Get start and end date of the semester from user
    start_date_str = input("Enter the semester start date (DD/MM/YYYY): ")
    end_date_str = input("Enter the semester end date (DD/MM/YYYY): ")

    # Get lecture days from user input
    lecture_days_input = input("Enter the lecture days (e.g., 0 for Monday, 2 for Wednesday, 4 for Friday, separated by commas): ")
    lecture_days = [int(day.strip()) for day in lecture_days_input.split(",")]

    # Path to the academic calendar PDF
    academic_calendar_path = "Academic_calendar_2024-25_sem1.pdf"

    # Generate the lecture schedule using the pre-extracted topics
    lecture_schedule = create_lecture_schedule(start_date_str, end_date_str, lecture_days, academic_calendar_path, topics_file)
    print(lecture_schedule)
