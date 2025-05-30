# Document Intake Service

This service handles the upload, parsing, and storage of applicant documents such as bank statements and Emirates ID images.

---

# Features

- Upload documents through a Streamlit UI.
- Supports PDF (bank statements) and image (Emirates ID) files.
- Processes files using a FastAPI backend.
- Parses and stores:
  - Bank statements in PostgreSQL.
  - Emirates ID images in MongoDB.

---

## 📦 Tech Stack

- Streamlit (Frontend)
- FastAPI (Backend)
- PostgreSQL
- MongoDB
- Python (Pandas, pdfplumber, easyocr)

---

##  Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/karishmac91/document_intake_system.git
cd document_intake_system

2. Set up virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

3. Install dependencies
pip install -r requirements.txt

4. Configure environment variables
POSTGRES_URI=postgresql://user:password@localhost:5432/dbname
MONGODB_URI=mongodb://localhost:27017

5. Run the services
Start FastAPI backend
uvicorn app.main:app --reload

6. Start Streamlit frontend
streamlit run streamlit_app.py


