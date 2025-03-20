import streamlit as st
from PIL import Image
from PyPDF2 import PdfReader
import docx
import google.generativeai as genai
import io
st.set_page_config(page_title="Legal Document Analyst App", layout="wide")
# ======================
#  SWANKY UI STYLING
# ======================
# Some simple CSS to enhance the look of the app. You can adjust colors, font, etc.
st.markdown(
    """
    <style>
    /* Import a classy, modern font */
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab&display=swap');

    /* Apply the font and a light background color to the whole app */
    html, body, [class*="css"] {
        font-family: 'Roboto Slab', serif;
        background-color: #f3f6f9;
    }

    /* Style the main content area */
    .main > div {
        background-color: #ffffff;
        padding: 2rem;
        margin: 1rem 0;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    /* Style headers */
    h1, h2, h3, h4 {
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }

    /* Style text areas and prompts */
    .stTextArea {
        border-radius: 8px;
        border: 1px solid #dcdcdc;
    }

    /* Boost the look of buttons */
    button[kind="primary"] {
        background-color: #1f77b4 !important;
        border-radius: 8px !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    /* Style the file uploader */
    .stFileUploader > label {
        color: #1f77b4;
        font-weight: 600;
    }

    .css-1fcdlh2 {
        background-color: #fafafa;
        border: 2px dashed #d3d3d3;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Configure the API key for Google Gemini
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Load Gemini Pro model
model = genai.GenerativeModel("gemini-1.5-flash")

# ============================
#   TEXT EXTRACTION FUNCTIONS
# ============================

def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = "\n".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = "\n".join([p.text for p in doc.paragraphs])
    return text

# ============================
#   GEMINI RESPONSE FUNCTIONS
# ============================

def get_gemini_response_text(content, prompt):
    response = model.generate_content([content, prompt])
    return response.text

def get_gemini_response_image(image, prompt):
    response = model.generate_content([image, prompt])
    return response.text

# ======================
#   STREAMLIT APP
# ======================


# Main heading
st.header("AI-Powered Legal Document Analyst")

# Brief description or disclaimer
st.markdown(
    """
    **Disclaimer:** This app provides generalized analysis of legal/policy documents. 
    It is **not** a substitute for professional legal counsel.
    """
)

# File upload section
uploaded_file = st.file_uploader(
    "Upload Your Legal/Policy Document (PDF, Word, or Image)",
    type=['pdf', 'docx', 'jpg', 'jpeg', 'png']
)

# Default Legal Analysis Prompt
default_prompt = (
    "You are an expert in analyzing legal and policy documents. "
    "Provide a thorough review, referencing relevant laws, regulations, or precedents. "
    "Summarize key arguments, identify potential issues or opportunities, "
    "and offer a reasoned perspective. Present your analysis in a structured, "
    "easy-to-read format using markdown. This does not constitute formal legal advice."
)

# Prompt customizer
prompt = st.text_area("Modify the AI Prompt (Optional)", value=default_prompt, height=200)

# Create layout with two columns
col1, col2 = st.columns([1, 2])

if uploaded_file:
    file_type = uploaded_file.type
    extracted_text = None

    # Handle PDFs
    if "pdf" in file_type:
        extracted_text = extract_text_from_pdf(uploaded_file)

    # Handle Word files
    elif "word" in file_type or "docx" in file_type:
        extracted_text = extract_text_from_docx(uploaded_file)

    # Handle Images
    elif "image" in file_type:
        try:
            image = Image.open(uploaded_file)
            st.sidebar.image(image, caption="Uploaded Image", use_column_width=True)
        except Exception as e:
            st.error(f"Error opening image: {e}")

    # Column 1: Display extracted text or the image
    with col1:
        st.subheader("Document Preview")
        if extracted_text:
            st.text_area("Extracted Text", value=extracted_text, height=400)
        elif "image" in file_type:
            st.image(image, caption="Uploaded Image", use_column_width=True)

    # Column 2: AI-generated suggestions
    with col2:
        st.subheader("AI-Powered Analysis & Suggestions")
        try:
            if extracted_text:
                response = get_gemini_response_text(extracted_text, prompt)
            elif "image" in file_type:
                response = get_gemini_response_image(image, prompt)
            st.markdown(response, unsafe_allow_html=False)
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Footer
st.sidebar.write("Powered by Google Gemini and Streamlit.")
