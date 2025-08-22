import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import os
import re
import json
import time


# --- Configuration ---
# Load API Key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Stopwords set for filtering common words in highlighting
STOPWORDS = {
    "the", "in", "with", "and", "or", "for", "to", "of", "a", "an", "is", "on",
    "by", "as", "at", "from", "that", "be", "are", "was", "were", "which", "this",
    "it", "has", "have", "will", "can", "should", "into", "but", "such", "their",
    "up", "over", "about", "not", "it's", "so", "if", "no", "etc"
}


# --- Core Functions ---


def extract_resume_text(uploaded_file):
    """Extracts and cleans text from an uploaded PDF file."""
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            # Clean up excessive whitespace and newlines for better processing
            page_text = re.sub(r'\s+', ' ', page_text).strip()
            text += page_text + " "
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None


def extract_json_from_response(response_text):
    """
    Extracts the first valid JSON object found in the response text.
    Handles code fences and text before/after JSON.
    """
    # Remove code fences/backticks
    cleaned = response_text.replace("``````", "").strip()
    # Find the first { and last } and attempt to extract JSON block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        json_text = match.group(0)
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            return None
    return None


def get_gemini_analysis(resume_text, job_description):
    """
    Calls the Gemini API with a detailed prompt to get a structured JSON response.
    This single call handles ATS score, feedback, keyword analysis, and data extraction.
    """
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # Enhanced prompt asking for a JSON output for reliable parsing
    prompt = f"""
    You are a highly sophisticated ATS (Applicant Tracking System) scanner and a professional recruitment consultant.
    Your task is to analyze the provided resume against the job description and return a structured JSON object.

    Analyze the following resume and job description:
    
    **Job Description:**
    ---
    {job_description}
    ---

    **Resume Text:**
    ---
    {resume_text}
    ---

    Please provide the following analysis in a single JSON object with the specified keys:
    1.  "ats_score": An integer percentage (0-100) representing how well the resume matches the job description.
    2.  "missing_keywords": A JSON array of important keywords or skills from the job description that are missing in the resume.
    3.  "feedback": A concise, constructive summary providing actionable advice to improve the resume for this specific job.
    4.  "extracted_skills": A JSON array of skills found in the resume.
    5.  "contact_info": A JSON object containing "emails" (an array of strings) and "phone_numbers" (an array of strings) extracted from the resume.

    **Example JSON Output:**
    {{
        "ats_score": 85,
        "missing_keywords": ["Project Management", "Agile Methodology", "Data Visualization"],
        "feedback": "The resume is strong but could be improved by quantifying achievements in past roles and adding a project section that highlights experience with Agile methodologies.",
        "extracted_skills": ["Python", "Streamlit", "Google Gemini API", "Regex"],
        "contact_info": {{
            "emails": ["example.email@domain.com"],
            "phone_numbers": ["+1234567890"]
        }}
    }}
    
    Now, generate the JSON output for the provided resume and job description.
    """

    try:
        response = model.generate_content(prompt)
        # Extract JSON from possible extra text or code fence
        analysis_result = extract_json_from_response(response.text)
        if not analysis_result:
            st.error(
                "The AI response could not be parsed as valid JSON. "
                "Please try again or check for any formatting issues."
            )
            st.info(f"Raw AI response (truncated):\n\n{response.text[:500]}")  # show beginning of AI response for debugging
            return None
        return analysis_result
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def get_keywords(job_description):
    """Extract keywords from job description filtering out stopwords and short words."""
    words = set(re.findall(r'\b\w+\b', job_description.lower()))
    filtered_keywords = {w for w in words if w not in STOPWORDS and len(w) > 2}
    return filtered_keywords


def highlight_keywords(resume_text, job_description):
    """Highlights important keywords from the job description found in the resume text."""
    keywords = get_keywords(job_description)
    if not keywords:
        return resume_text

    # Build regex pattern to match whole keywords, case-insensitive
    pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in keywords) + r')\b', flags=re.IGNORECASE)

    # Highlight matched keywords with HTML span
    highlighted_text = pattern.sub(
        lambda match: f"<span style='background-color: #FFF59D; color: #000000;'>{match.group(0)}</span>",
        resume_text
    )
    return highlighted_text


# --- Streamlit UI ---

def main():
    st.set_page_config(page_title="ATS Resume Expert", layout="wide")

    # Custom CSS for clean, professional design
    st.markdown(
        """
        <style>
            /* Background color */
            .stApp {
                background-color: #F5F7FA;
                color: #323232;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            /* Page title */
            .css-1d391kg h1 {
                color: #003366;
            }

            /* Sidebar styling */
            .css-1d391kg .css-1v3fvcr {
                background-color: #FFFFFF;
                border-right: 2px solid #E1E5EB;
            }

            /* Buttons */
            div.stButton > button:first-child {
                background-color: #005A9C;
                color: white;
                font-weight: 600;
            }

            div.stButton > button:first-child:hover {
                background-color: #004080;
                color: white;
            }

            /* Input text area */
            textarea, input[type="text"] {
                background-color: #FFFFFF;
                border: 1px solid #B0B8C1;
                color: #323232;
            }

            /* Highlight keyword background */
            span {
                border-radius: 3px;
                padding: 0 3px;
            }

            /* Metrics style */
            .stMetric > div > div {
                font-weight: 700;
                color: #004080;
            }

            /* Feedback box */
            .stInfo {
                background-color: #E3F2FD;
                border-left: 5px solid #1976D2;
            }

            /* Headers */
            h2, h3 {
                color: #003366;
            }

            /* Markdown links */
            a {
                color: #005A9C;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }

        </style>
        """,
        unsafe_allow_html=True
    )

    # --- Header ---
    st.title("ATS Resume Expert")
    st.markdown(
        "Get an instant, professional analysis of your resume against a job description. "
        "Receive your ATS score, detailed feedback, and discover any missing keywords."
    )

    # --- Input Fields ---
    st.sidebar.header("Inputs")
    job_description = st.sidebar.text_area("Paste the Job Description Here", height=250, key="job_desc")
    uploaded_file = st.sidebar.file_uploader("Upload Your Resume (PDF)", type=["pdf"], key="resume_upload")

    col1, col2 = st.columns([1, 1])

    with col1:
        analyze_button = st.button("Analyze Resume", use_container_width=True, type="primary")
    with col2:
        highlight_button = st.button("Highlight Keywords", use_container_width=True)

    # --- Main Logic ---
    if analyze_button:
        if uploaded_file is None or not job_description.strip():
            st.warning("Please upload a resume and paste a job description to proceed.")
        else:
            with st.spinner("Reading your resume..."):
                resume_text = extract_resume_text(uploaded_file)

            if resume_text:
                st.info("Resume parsed successfully. Contacting AI for analysis...")

                # Progress bar animation
                progress_bar = st.progress(0, text="Analyzing...")

                analysis_result = get_gemini_analysis(resume_text, job_description)

                for percent_complete in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(percent_complete + 1, text="Finalizing report...")
                progress_bar.empty()

                if analysis_result:
                    st.success("Analysis Complete")

                    st.subheader("Your Resume Analysis Report")

                    score_col, contact_col = st.columns(2)
                    with score_col:
                        st.metric(label="ATS Match Score", value=f"{analysis_result.get('ats_score', 0)}%")
                    with contact_col:
                        contact = analysis_result.get('contact_info', {})
                        st.write("Emails:", ", ".join(contact.get('emails', ["Not Found"])))
                        st.write("Phone Numbers:", ", ".join(contact.get('phone_numbers', ["Not Found"])))

                    st.markdown("---")

                    st.markdown("### Constructive Feedback")
                    st.info(analysis_result.get('feedback', "No feedback provided."))

                    keywords_col, skills_col = st.columns(2)
                    with keywords_col:
                        st.markdown("Missing Keywords")
                        missing_keywords = analysis_result.get('missing_keywords', [])
                        if missing_keywords:
                            for keyword in missing_keywords:
                                st.markdown(f"- {keyword}")
                        else:
                            st.write("No critical keywords are missing.")

                    with skills_col:
                        st.markdown("Skills Found in Resume")
                        extracted_skills = analysis_result.get('extracted_skills', [])
                        if extracted_skills:
                            st.write(", ".join(extracted_skills))
                        else:
                            st.write("No specific skills section detected.")
                else:
                    st.error(
                        "Unable to process resume analysis due to AI response format. "
                        "Please try again or use a different resume format."
                    )

    if highlight_button:
        if uploaded_file is not None and job_description.strip():
            resume_text = extract_resume_text(uploaded_file)
            if resume_text:
                st.subheader("Resume with Highlighted Keywords")
                highlighted_text = highlight_keywords(resume_text, job_description)
                st.markdown(highlighted_text, unsafe_allow_html=True)
        else:
            st.warning("Please upload a resume and provide a job description to highlight keywords.")


if __name__ == "__main__":
    main()
