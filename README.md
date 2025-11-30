# Smart Task Analyzer

## Setup (Windows PowerShell)
1. Clone repo
2. Create & activate venv:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt

## Run Backend
cd backend
python manage.py migrate
python manage.py runserver 127.0.0.1:8001

## Run Frontend
cd frontend
npm install
npm run dev

