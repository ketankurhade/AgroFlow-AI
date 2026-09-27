# AgroFlow AI - Backend

FastAPI & PostgreSQL backend for the AgroFlow AI Supply Chain Management system.

## Setup Instructions

1. **Create and Activate Virtual Environment:**
   ```bash
   cd backend
   python -m venv .venv
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   # Linux/macOS:
   source .venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Copy `.env.example` to `.env` and set your local PostgreSQL password:
   ```env
   DATABASE_URL=postgresql://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/agroflow
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ALLOWED_ORIGINS=http://localhost:5173
   ```

4. **Seed Sample Data (Optional):**
   ```bash
   python seed.py
   ```

5. **Run FastAPI Server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

6. **Interactive Documentation:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`
