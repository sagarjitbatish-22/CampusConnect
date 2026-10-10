# CampusConnect
CampusConnect is a simple web app where students easily report and view campus issues like broken fans, Wi-Fi problems, or lost items. Students can register, login, submit issues with a title, description and category, and track status from Open to In Progress to Resolved. Built with HTML, CSS, JavaScript, FastAPI and SQLite by a team using GitHub.

## Features
- Register and log in (token based)
- Dashboard showing all reported issues from the database
- Report a new issue with a title, description and category
- Open an issue to see its details and update its status (Open, In Progress, Resolved)

## Technologies
- Frontend: HTML, CSS, JavaScript (fetch API)
- Backend: Python, FastAPI
- Database: SQLite

## How to Run

### 1. Backend
1. Open a terminal in the project folder (the one with main.py)
2. Create a virtual environment: python -m venv venv
3. Activate it: venv\Scripts\activate
4. Install packages: pip install -r requirements.txt
5. Start the server: python -m uvicorn main:app --reload
6. Open http://127.0.0.1:8000/docs to test the APIs

### 2. Frontend
Keep the backend running, then open a second terminal in the same folder and run:

python -m http.server 5500

Open http://127.0.0.1:5500/login.html in your browser. (VS Code Live Server also works.)
Register an account first, then log in.

## API Endpoints
| Method | Endpoint | What it does |
|---|---|---|
| POST | /register | Create an account |
| POST | /login | Log in and get a token |
| GET | /me | Get profile details |
| GET | /categories | List issue categories |
| POST | /issues | Create an issue |
| GET | /issues | List all issues |
| GET | /issues/{id} | Get issue details |
| PUT | /issues/{id}/status | Update issue status |

All /issues and /me endpoints need a logged-in user (the frontend sends the token automatically).

## Team Members
1. Sagarjit Singh Batish(Backend+Database)
2. Prikshit Goel(Frontend)
3. Parleen Cheema(Intergration+Testing)
