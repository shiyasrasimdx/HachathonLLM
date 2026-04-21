import streamlit as st
import docx
import os
from pypdf import PdfReader
import io
import time
import json
from groq import Groq
from dotenv import load_dotenv

# --- Load API Key ---
load_dotenv()
GROQ_API_KEY = os.getenv("groq_API")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# --- Page Configuration ---
st.set_page_config(page_title="AI Resume Matcher", page_icon="🚀", layout="wide")

# --- Custom Styling ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0f172a;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #fbbf24 !important;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #fbbf24;
        color: #0f172a;
        font-weight: bold;
        font-size: 1.1rem;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #f59e0b;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3);
    }
    .upload-card {
        background-color: #1e293b;
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid #334155;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Functions ---
def get_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content
        return text
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    return ""

def analyze_with_ai(resume_text, jd_text):
    if not client:
        return {
            "score": 0, 
            "matched": ["API Key Missing"], 
            "missing": ["Please configure groq_API in .env"],
            "suggestion": "Contact support or add your API key."
        }
    
    prompt = f"""
    You are an expert ATS (Applicant Tracking System).
    Analyze the following Resume against the Job Description.
    
    Resume:
    {resume_text[:4000]}
    
    Job Description:
    {jd_text[:4000]}
    
    Return a valid JSON object with the following structure:
    {{
        "score": (integer 0-100),
        "matched": [(list of 5-8 key matching skills/keywords)],
        "missing": [(list of 5-8 missing key skills/keywords)],
        "suggestion": "string (one short actionable tip to improve the resume)"
    }}
    Do not include any other text in your response. Ensure the output is strictly valid JSON.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        return {
            "score": 0, 
            "matched": ["Error"], 
            "missing": [str(e)], 
            "suggestion": "Please try again or check your internet connection."
        }

@st.dialog("ATS Analysis Result")
def show_score(analysis):
    score = analysis.get("score", 0)
    matched = analysis.get("matched", [])
    missing = analysis.get("missing", [])
    suggestion = analysis.get("suggestion", "Keep improving your profile!")

    st.write(f"## Overall Match: **{score}%**")
    st.progress(score / 100)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✅ Matched Skills")
        for s in matched[:8]:
            st.write(f"- {s}")
            
    with col2:
        st.subheader("❌ Missing Keywords")
        for s in missing[:8]:
            st.write(f"- {s}")
            
    st.divider()
    st.info(f"💡 **Tip:** {suggestion}")
    
    if st.button("Close"):
        st.rerun()

# --- Main UI ---
st.title("🚀 AI Resume Matcher")
st.markdown("#### Optimize your resume for Applicant Tracking Systems using Groq Llama-3 AI.")

st.write("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.write("### 📝 Job Description")
    jd_file = st.file_uploader("Upload Job Description", type=["pdf", "docx"], key="jd_upload")
    jd_text_input = st.text_area("Or paste JD text here...", height=150, key="jd_text")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.write("### 📄 Your Resume")
    resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx"], key="resume_upload")
    st.write("\n" * 7) # Spacer to align
    st.markdown('</div>', unsafe_allow_html=True)

st.write("\n" * 2)

if st.button("Analyze Now"):
    # Extract text
    resume_text = get_text_from_file(resume_file)
    final_jd_text = jd_text_input if jd_text_input else get_text_from_file(jd_file)
    
    if not resume_text:
        st.error("Please upload your resume to start.")
    elif not final_jd_text:
        st.error("Please provide a job description.")
    else:
        with st.spinner("🚀 AI is analyzing your profile using Llama-3..."):
            # Real AI Analysis
            analysis_result = analyze_with_ai(resume_text, final_jd_text)
            show_score(analysis_result)

# --- Footer ---
st.write("\n" * 10)
st.markdown("""
    <div style='text-align: center; color: #64748b; font-size: 0.8rem;'>
        Powered by Groq AI | Built for Hackathon 2026
    </div>
    """, unsafe_allow_html=True)