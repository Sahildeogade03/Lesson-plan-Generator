import fitz  # PyMuPDF
import re

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

    return "\n".join(final_topics)

# Function to save topics to a text file
def save_topics_to_file(topics, file_name="extracted_topics.txt"):
    with open(file_name, "w") as file:
        file.write(topics)
    print(f"Topics successfully saved to {file_name}")

# Function to load topics from a text file
def load_topics_from_file(file_name="extracted_topics.txt"):
    with open(file_name, "r") as file:
        topics = file.read()
    return topics

# Function to split chapters and subtopics
def split_chapters_and_subtopics(cleaned_text):
    chapters = {}
    lines = cleaned_text.splitlines()
    current_chapter = None

    for line in lines:
        stripped_line = line.strip()
        print(f"Processing line: {stripped_line}")  # Debugging print statement

        # Generalized logic for detecting chapter headings
        # We treat a line as a chapter heading if it's relatively short and doesn't contain punctuation (commas, colons, hyphens)
        if len(stripped_line.split()) <= 6 and not re.search(r'[,:-]', stripped_line):
            current_chapter = stripped_line
            chapters[current_chapter] = []
            print(f"Found chapter: {current_chapter}")  # Debugging print statement
        elif current_chapter and stripped_line:  # Ensure we only add subtopics if a chapter heading exists
            # Avoid adding lecture headers or empty lines as subtopics
            if not (len(stripped_line.split()) <= 6 and not re.search(r'[,:-]', stripped_line)):
                subtopics = [subtopic.strip() for subtopic in stripped_line.split(',') if subtopic.strip()]
                chapters[current_chapter].extend(subtopics)
                print(f"Added subtopics: {subtopics}")  # Debugging print statement

    return chapters

# Function to split subtopics into lectures
def split_into_lectures(chapters, subtopics_per_lecture=2):
    lectures = []
    
    for chapter, subtopics in chapters.items():
        current_lecture = []
        for i, subtopic in enumerate(subtopics, start=1):
            current_lecture.append(subtopic)
            # Assign subtopics per lecture based on the given limit
            if len(current_lecture) == subtopics_per_lecture or i == len(subtopics):
                lectures.append((chapter, current_lecture))
                current_lecture = []
    
    return lectures

# Function to save lecture plan to a text file
def save_lecture_plan_to_file(lectures, file_name="organized_lectures.txt"):
    with open(file_name, "w") as file:
        lecture_count = 1
        for chapter, lecture_subtopics in lectures:
            file.write(f"Lecture {lecture_count} ({chapter}):\n")
            for subtopic in lecture_subtopics:
                file.write(f"  - {subtopic}\n")
            file.write("\n")
            lecture_count += 1
    print(f"Lecture plan successfully saved to {file_name}")

# Function to print lecture plan (optional)
def print_lecture_plan(lectures):
    lecture_count = 1
    for chapter, lecture_subtopics in lectures:
        print(f"Lecture {lecture_count} ({chapter}):")
        for subtopic in lecture_subtopics:
            print(f"  - {subtopic}")
        print()
        lecture_count += 1

# Main function to generate lecture plan from file
def generate_lecture_plan_from_file(file_name="extracted_topics.txt", subtopics_per_lecture=2):
    topics = load_topics_from_file(file_name)

    chapters = split_chapters_and_subtopics(topics)
    lectures = split_into_lectures(chapters, subtopics_per_lecture)
    
    # Save organized lectures to a text file
    save_lecture_plan_to_file(lectures, "organized_lectures.txt")

# Main function to parse the PDF, extract topics, save them, and generate lecture plan
if __name__ == "__main__":
    # Replace with the path to your PDF file
    pdf_path = "SYLLABUS.pdf"

    # Replace with the subject name you want to search for
    subject_name = input("Enter the subject name: ")

    pdf_text = extract_text_from_pdf(pdf_path)
    topics = extract_topics_for_subject(pdf_text, subject_name)

    if "not found" in topics:
        print(topics)
    else:
        save_topics_to_file(topics)
        generate_lecture_plan_from_file("extracted_topics.txt", subtopics_per_lecture=3)
