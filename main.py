import streamlit as st
from PIL import Image
from PyPDF2 import PdfReader
import docx
import google.generativeai as genai
import io

# Set up Streamlit page
st.set_page_config(page_title="Legal Document Analyst App", layout="wide")


st.markdown(
    """
    <style>
    /* Import a classy, modern font */
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab&display=swap');

    /* 
       Overall theme:
       - A repeating diagonal gradient background
       - Clean white container area
       - Subtle drop shadows
       - Accented text and buttons
     */

    /* Page background pattern */
    body {
        background: repeating-linear-gradient(
            45deg,
            #f3f6f9,
            #f3f6f9 20px,
            #e2e8ef 20px,
            #e2e8ef 40px
        ) !important;
        background-attachment: fixed;
    }
    
    /* Use Roboto Slab for a modern look */
    html, body, [class*="css"]  {
        font-family: 'Roboto Slab', serif;
        /* The repeating gradient above sets the background pattern */
        margin: 0;
        padding: 0;
    }

    /* Main content area styling (the 'cards') */
    .main > div {
        background-color: #ffffff;
        padding: 2rem;
        margin: 1rem 0;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    /* Headers styling */
    h1, h2, h3, h4 {
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }

    /* Style text areas and inputs */
    .stTextArea, .stTextInput {
        border-radius: 8px;
        border: 1px solid #dcdcdc;
    }

    /* Stylish buttons */
    button[kind="primary"] {
        background-color: #1f77b4 !important;
        border-radius: 8px !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    /* File uploader area */
    .stFileUploader > label {
        color: #1f77b4;
        font-weight: 600;
    }

    /* Make the file uploader box stand out */
    .css-1fcdlh2 {
        background-color: #fafafa;
        border: 2px dashed #d3d3d3;
    }

    /* Sidebar styling: a slightly opaque background overlay */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* Tweak sidebar headings, etc. */
    .css-h4m289 {
        color: #2c3e50 !important;
    }

    /* Optional: Hide Streamlit branding, menu (if desired) */
    /* .css-1lsmgbg e1fqkh3o1 { visibility: hidden; } */
    /* .css-1f9o3k2 { visibility: hidden; } */
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
    Discover the future of legal review with our cutting-edge **AI-powered Legal Document Analyst** platform. Upload any document and instantly receive concise, expertly curated insights, from key clauses to strategic implications. Enjoy a sleek, intuitive interface, rapid text extraction, and on-demand bullet-point summaries—all designed to streamline complex legal work and delight your workflow.
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

# We’ll always use the default prompt for the main analysis
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
