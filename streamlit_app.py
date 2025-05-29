import streamlit as st
import requests

st.set_page_config(page_title="Document Intake System", layout="centered")
st.title("📄 Upload Financial Documents")

st.markdown("""
Upload the following documents:
- 🏦 Bank Statement  
- 🪪 Emirates ID  
- 📄 Resume  
- 📊 Assets/Liabilities (Excel)  
- 🧾 Credit Report  
""")

uploaded_files = st.file_uploader("Upload your documents", type=["pdf", "docx", "xlsx", "csv", "jpg", "png"], accept_multiple_files=True)

if st.button("Submit") and uploaded_files:
    with st.spinner("Uploading..."):
        files = [("files", (file.name, file, file.type)) for file in uploaded_files]
        print("Files to upload:", files)  # Debugging line to check uploaded files
    # Send files to the FastAPI backend
        response = requests.post("http://localhost:8000/upload/", files=files)

    if response.status_code == 200:
        result = response.json()


        print("Response from server:", result)  # Debugging line to check server response
        st.success("Documents processed successfully!")
    else:
        st.error("Error processing the document. Please try again.")
