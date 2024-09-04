import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import re

load_dotenv()  # Load all environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

def clean_response(response):
    response = response.replace("'", '"')
    response = re.sub(r'\s+', ' ', response).strip()
    return response

# Prompt Template

input_prompt = """
Hey, act like a highly skilled and expert ATS (Applicant Tracking System) evaluator with extensive experience in resume analysis. 
You are a highly qualified entity in all fields of computer science, including software engineering, data science,
data analysis, and big data engineering, Web development, app development. Your task is to evaluate the resume based on the given job
description. You must consider the highly competitive job market and provide the best assistance 
for improving the resumes. Assign a percentage match based on the job description and identify
the missing keywords with high accuracy.

resume: {text}
description: {jd}

I want the response in a single string with the following structure:
{{"JD Match": "%", "MissingKeywords": [], "Profile Summary": ""}}
"""


# Custom HTML for the header with a visible image
st.markdown(
    """
    <style>
    .header-container {
        padding: 20px;
        text-align: center;
        color: black;
        position: relative;
    }
    .header-container img {
        width: 100%;
        max-height: 150px;
        object-fit: cover;
        # opacity: 0.8;
    }
    .header-title {
        font-size: 32px;
        font-weight: bold;
        margin: 0;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    </style>
    <div class="header-container">
        <img src="https://miro.medium.com/v2/resize:fit:1200/1*gU95zElQsI57LTLdicOoTQ.png" alt="Gemini Logo">
    </div>
    <div class="header-container">
        <h1 class="header-title">Gemini ATS Evaluator</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Streamlit app content
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the pdf")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        formatted_prompt = input_prompt.format(text=text, jd=jd)
        response = get_gemini_response(formatted_prompt)

        cleaned_response = clean_response(response)
        
        try:
            response_data = json.loads(cleaned_response)
            st.subheader("Evaluation Results")
            
            # Display Job Description Match
            st.markdown(f"**Job Description Match:** {response_data['JD Match']}")
            
            # Display Missing Keywords
            st.markdown("**Missing Keywords:**")
            st.write(", ".join(response_data["MissingKeywords"]))
            
            # Display Profile Summary
            st.markdown("**Profile Summary:**")
            st.write(response_data["Profile Summary"])

        except json.JSONDecodeError:
            st.error("Failed to parse the response. The format might be incorrect.")
            st.text_area("Raw Response", value=response)

