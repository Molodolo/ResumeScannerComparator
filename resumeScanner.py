import spacy
import PyPDF2
import docx
import os
import requests
from bs4 import BeautifulSoup


def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text


def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def extract_keywords(text):
    doc = nlp(text.lower())

    # Remove stop words and punctuation
    words = [token.text for token in doc if not token.is_stop and not token.is_punct]

    # Extract entities
    entities = [ent.text for ent in doc.ents]

    # Extract noun chunks
    noun_chunks = [chunk.text for chunk in doc.noun_chunks]

    # Combine words, entities, and noun chunks
    keywords = list(set(words + entities + noun_chunks))

    return keywords


def calculate_matching_score(resume_keywords, job_keywords):
    matching_keywords = set(resume_keywords) & set(job_keywords)
    score = len(matching_keywords) / len(job_keywords)
    return score


def process_resume(resume_file, job_keywords):
    file_extension = os.path.splitext(resume_file)[1].lower()
    if file_extension == ".pdf":
        resume_text = extract_text_from_pdf(resume_file)
    elif file_extension == ".docx":
        resume_text = extract_text_from_docx(resume_file)
    else:
        print(f"Unsupported file format: {file_extension}")
        return None

    resume_keywords = extract_keywords(resume_text)
    matching_score = calculate_matching_score(resume_keywords, job_keywords)
    return matching_score, resume_keywords


def download_job_description(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # Find the requirements or qualifications section
        requirements_section = None
        for header in soup.find_all(["h2", "h3", "h4", "h5", "h6"]):
            if "requirements" in header.text.lower() or "qualifications" in header.text.lower():
                requirements_section = header.find_next("ul")
                break

        if requirements_section:
            requirements_text = " ".join(
                [li.text for li in requirements_section.find_all("li")])
            return requirements_text
        else:
            print("Requirements or qualifications section not found on the webpage.")
            print("Extracting keywords from the entire webpage instead.")
            webpage_text = soup.get_text()
            return webpage_text
    else:
        print(
            f"Failed to download the webpage. Status code: {response.status_code}")
        return None


def main():
    global nlp
    nlp = spacy.load("en_core_web_lg")

    job_url = input("Enter the URL of the job webpage: ")
    job_description = download_job_description(job_url)

    if job_description:
        job_keywords = extract_keywords(job_description)
        print("Job Description Keywords:")
        print(job_keywords)
        print()

        resume_file = input("Enter the path to the resume file: ")
        file_extension = os.path.splitext(resume_file)[1].lower()
        matching_score, resume_keywords = process_resume(
            resume_file, job_keywords)

        if matching_score is not None:
            print("Matching Score:", matching_score)
            print()
            print("Resume Keywords:")
            print(resume_keywords)
            print()
            print("Matching Keywords:")
            print(set(resume_keywords) & set(job_keywords))
    else:
        print("Failed to retrieve the job description.")


if __name__ == "__main__":
    main()
