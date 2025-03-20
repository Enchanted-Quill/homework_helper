import streamlit as st
from PIL import Image
from PyPDF2 import PdfReader
import docx
import google.generativeai as genai
import io

# Set up Streamlit page
st.set_page_config(page_title="Legal Document Analyst App", layout="wide")

# ===============================
#   SWANKY AF UI STYLING (CSS)
# ===============================
st.markdown(
    """
    <style>
    /* 
      1) Animated Gradient Background
      2) Frosted Glass Container
      3) Neon Glow Text
      4) Elevated Buttons
    */

    /* 
       1) ANIMATED GRADIENT BACKGROUND 
         - We'll make the entire page swirl through colors over 12s
    */
    body {
        background: linear-gradient(135deg, #EF5DA8, #845EF7, #5D5FEF, #EF895D);
        background-size: 400% 400%;
        animation: gradient-bg 12s ease infinite;
        margin: 0;
        padding: 0;
    }
    @keyframes gradient-bg {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 
       2) FROSTED GLASS CONTAINER 
         - The .main > div target includes our Streamlit "card" containers.
         - We'll add a backdrop-filter for a 'glass' effect plus a translucent background.
    */
    .main > div {
        background-color: rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(12px);
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        color: #fff;
        margin: 1rem 0;
        padding: 2rem;
    }

    /* 
       3) NEON GLOW HEADINGS 
         - We'll give the headings a subtle neon glow and bright color
    */
    h1, h2, h3, h4 {
        color: #ffffff;
        text-shadow:
          0 0 6px rgba(255, 255, 255, 0.5),
          0 0 12px rgba(255, 255, 255, 0.3);
        margin-bottom: 1rem;
    }

    /* 
       Use a clean modern font
    */
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Roboto Slab', serif;
    }

    /* 
       Inputs and text areas with a subtle glow / frosted effect as well
    */
    .stTextArea, .stTextInput, .css-19ih76x, .css-ffhzg2, .css-1r51q1k {
        background-color: rgba(255, 255, 255, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 10px !important;
        color: #fff !important;
    }

    /* 
       4) ELEVATED PRIMARY BUTTONS 
    */
    button[kind="primary"] {
        background: linear-gradient(135deg, #845EF7 0%, #5D5FEF 100%) !important;
        border: none !important;
        color: #fff !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: transform 0.2s ease;
    }
    button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.4);
    }

    /* 
       File Uploader 
    */
    .stFileUploader > label {
        color: #ffffff;
        font-weight: 600;
    }
    .css-1fcdlh2 {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border: 2px dashed rgba(255, 255, 255, 0.4) !important;
    }

    /* 
       SIDEBAR 
         - Make it partially transparent to show off the background
    */
    .css-1d391kg {
        background-color: rgba(0, 0, 0, 0.3) !important;
        backdrop-filter: blur(10px);
    }
    .css-h4m289 {
        color: #ffffff !important;
    }

    /* 
       We'll also ensure normal text is more readable
    */
    .stMarkdown, .stText, .stRadio, .css-1h2q7hz {
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ======================
#   CONFIGURE GEMINI
# ======================
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
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

# ================================
#   SUMMARIZATION FUNCTION
# ================================
def get_short_summary(content):
    """
    Generate a concise bullet-point summary
    based on the extracted content.
    """
    summary_prompt = (
        "Please provide a concise bullet-point summary of the main points or arguments "
        "in this legal/policy document. Keep it under 150 words."
    )
    return get_gemini_response_text(content, summary_prompt)

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

# We'll always use the default prompt for the main analysis
prompt = default_prompt

# Layout with two columns
col1, col2 = st.columns([1, 2])

if uploaded_file:
    file_type = uploaded_file.type
    extracted_text = None

    # Handle PDF
    if "pdf" in file_type:
        extracted_text = extract_text_from_pdf(uploaded_file)
    # Handle Word
    elif "word" in file_type or "docx" in file_type:
        extracted_text = extract_text_from_docx(uploaded_file)
    # Handle Images
    elif "image" in file_type:
        try:
            image = Image.open(uploaded_file)
            st.sidebar.image(image, caption="Uploaded Image", use_column_width=True)
        except Exception as e:
            st.error(f"Error opening image: {e}")

    # Column 1: Document Preview
    with col1:
        st.subheader("Document Preview")
        if extracted_text:
            st.text_area("Extracted Text", value=extracted_text, height=400)
        elif "image" in file_type:
            st.image(image, caption="Uploaded Image", use_column_width=True)

    # Column 2: AI-Powered Analysis
    with col2:
        st.subheader("AI-Powered Analysis & Suggestions")
        try:
            if extracted_text:
                response = get_gemini_response_text(extracted_text, prompt)
            else:
                # Generate response for image-based content
                response = get_gemini_response_image(image, prompt)
            st.markdown(response, unsafe_allow_html=False)
        except Exception as e:
            st.error(f"An error occurred: {e}")

    # ======================
    #   SIDEBAR SUMMARY
    # ======================
    if extracted_text:
        with st.sidebar:
            st.markdown("## Quick Summary")
            try:
                summary = get_short_summary(extracted_text)
                st.write(summary)
            except Exception as e:
                st.write("Unable to generate summary.")

# Trademarks/Credits on Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Trademarks & Credits")
st.sidebar.write(
    "© 2025 **BetterMind Labs**. All trademarks are property of their respective owners."
)
st.sidebar.write(
    "Developed with [Google Gemini](https://cloud.google.com/genai) & [Streamlit](https://streamlit.io/)."
)
