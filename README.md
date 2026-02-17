# AI Based Internship Shortlisting Portal

A Django + React platform that helps colleges and faculty shortlist internship applicants using NLP-based resume parsing and semantic matching. Students apply with a PDF resume and academic details, and teachers can post opportunities, review applicants, and export results.

## Tech Stack
- Backend: Django 4, Django REST Framework, JWT
- Frontend: React 18, Vite, Bootstrap 5
- Database: PostgreSQL
- ML/NLP: spaCy, sentence-transformers, scikit-learn

## Features
- Role-based access for students and teachers
- Resume parsing with skill extraction and semantic scoring
- Teacher dashboard with analytics and exports
- Student dashboard to apply and track application status
- Explainable shortlisting scores

## Setup
### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL

### Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
Copy-Item ..\.env.example .env
# Update backend\.env with PostgreSQL credentials
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

### URLs
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/api/`
- Admin: `http://localhost:8000/admin/`

## Contributing
1. Fork this repository to your GitHub account.
2. Clone your fork locally: `git clone https://github.com/<your-username>/<repo-name>.git`
3. Add original repo as upstream:
   `git remote add upstream https://github.com/<original-owner>/<repo-name>.git`
4. Create a feature branch: `git checkout -b feature/my-change`
5. Make changes and commit: `git add . && git commit -m "feat: short description"`
6. Push your branch: `git push origin feature/my-change`
7. Open a pull request from your fork branch to the upstream repository `main` branch.

## Push To GitHub
1. Initialize Git if this folder is not a repo yet:
   `git init`
2. Add files and commit:
   `git add .`
   `git commit -m "Initial commit"`
3. Create a new empty GitHub repository.
4. Add remote origin:
   `git remote add origin https://github.com/<your-username>/<repo-name>.git`
5. Push branch:
   `git branch -M main`
   `git push -u origin main`
6. For later updates:
   `git add .`
   `git commit -m "your message"`
   `git push`

## Notes
- Resume uploads must be PDF (text-based, not scanned).
- ML models download on first use.
