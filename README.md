# Resume-Screener

A professional Applicant Tracking System (ATS) Resume Screener built with Streamlit and Google Gemini AI. This web app helps job applicants instantly evaluate their resume's compatibility against any job description by providing an ATS match score, actionable feedback, highlighted keywords, and detected contact info.

---

## Live Demo

Try the live, deployed app here:  
[https://resume-screener-ats.streamlit.app/](https://resume-screener-ats.streamlit.app/)

---

## Features

- Upload your resume in PDF format and paste any job description.
- Receive an ATS match score indicating how well your resume fits the job.
- Get AI-generated, actionable feedback to improve your resume.
- See keywords missing from your resume compared to the job description.
- Extract key skills found in your resume and highlight keywords for easy review.
- Extract emails and phone numbers from your resume.

---

## Technologies

- Python 3.7+
- Streamlit for the web app interface
- Google Generative AI (Gemini API) for resume analysis
- PyPDF2 for PDF text extraction
- dotenv for environment variable management

---

## Installation & Usage

1. Clone the repository:
```
git clone https://github.com/krish-117/Resume-Screener.git
cd Resume-Screener
```

3. Create and activate a virtual environment (optional but recommended):
```
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

4. Install dependencies:
```
pip install -r requirements.txt
```

5. Create a `.env` file in the root directory with your Google API key:
```
GOOGLE_API_KEY="your_google_api_key_here"
```

6. Run the Streamlit app:
```
streamlit run app.py
```

7. In the opened browser window, paste your job description and upload your resume PDF to start analyzing.

---

## Deployment

The app can be deployed easily on [Streamlit Cloud](https://streamlit.io/cloud) or other cloud platforms. 

**For Streamlit Cloud:**

- Push your code to GitHub.
- Connect your repo on Streamlit Cloud.
- Add your `GOOGLE_API_KEY` as a secret environment variable.
- Deploy with one click!

---

## Contributing

Contributions and suggestions are welcome. Please open issues or submit pull requests for improvements.


---

## Contact

For questions or feedback, please reach out at:  
`krishdobariya117@gmail.com`
