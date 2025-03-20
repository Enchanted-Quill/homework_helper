import streamlit as st
from PIL import Image
from PyPDF2 import PdfReader
import docx
import google.generativeai as genai
import io

# Configure the API key for Google Gemini
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Load Gemini Pro model
model = genai.GenerativeModel("gemini-1.5-flash")


# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = "\n".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
    return text


# Function to extract text from Word documents
def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = "\n".join([p.text for p in doc.paragraphs])
    return text


# Function to generate Gemini response for text-based inputs (PDF/Word)
def get_gemini_response_text(content, prompt):
    response = model.generate_content([content, prompt])
    return response.text


# Function to generate Gemini response for image-based inputs
def get_gemini_response_image(image, prompt):
    response = model.generate_content([image, prompt])
    return response.text

#Streamlit app configuration
st.set_page_config(page_title="Homework Completion App", layout="wide")
st.header("AI-Powered Homework Completion App")

# File upload
uploaded_file = st.file_uploader("Upload Your File (PDF, Word, or Image)", type=['pdf', 'docx', 'jpg', 'jpeg', 'png'])

# Default homework completion prompt
default_prompt = (
    "You are an expert in assisting students with their homework. Your task is to provide a complete, detailed, and helpful "
    "answer to the provided content, formatted in markdown. Include:\n\n"
    "- Key points summarized from the content.\n"
    "- Answers to any questions detected in the content.\n"
    "- Additional insights, examples, or suggestions to improve the completeness of the homework.\n"
    "- Maintain a student-friendly tone and clear markdown formatting for readability.\n"
)

prompt = st.text_area("Modify the AI Prompt (Optional)", value=default_prompt, height=200)

# Layout split into two columns
col1, col2 = st.columns([1, 2])

if uploaded_file:
    file_type = uploaded_file.type
    extracted_text = None

    # Handle PDF files
    if "pdf" in file_type:
        extracted_text = extract_text_from_pdf(uploaded_file)
    # Handle Word files
    elif "word" in file_type or "docx" in file_type:
        extracted_text = extract_text_from_docx(uploaded_file)
    # Handle Image files
    elif "image" in file_type:
        try:
            image = Image.open(uploaded_file)
            st.sidebar.image(image, caption="Uploaded Image", use_column_width=True)
        except Exception as e:
            st.error(f"Error opening image: {e}")

    # Display extracted content or image
    with col1:
        st.subheader("Extracted Content")
        if extracted_text:
            st.text_area("Content", value=extracted_text, height=400)
        elif "image" in file_type:
            st.image(image, caption="Uploaded Image", use_column_width=True)

    # Generate AI-powered suggestions
    with col2:
        st.subheader("AI-Powered Suggestions")
        try:
            if extracted_text:
                # Generate response for text-based content
                response = get_gemini_response_text(extracted_text, prompt)
            elif "image" in file_type:
                # Generate response for image-based content
                response = get_gemini_response_image(image, prompt)
            st.markdown(response, unsafe_allow_html=False)
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Footer
st.sidebar.write("Powered by Google Gemini and Streamlit.")

