# CampusConnect
CampusConnect is a simple web app where students easily report and view campus issues like broken fans, Wi-Fi problems, or lost items. Students can register, login, submit issues with a title, description and category, and track status from Open to In Progress to Resolved. Built with HTML, CSS, JavaScript, FastAPI and SQLite by a team using GitHub.
Add backend setup and run instructions to README
Document API endpoints in README

## How to Run the Backend
1. Go to the backend folder: cd backend
2. Create a virtual environment: python -m venv venv
3. Activate it: venv\Scripts\activate
4. Install packages: pip install -r requirements.txt
5. Start the server: python -m uvicorn main:app --reload
6. Open http://127.0.0.1:8000/docs to test the APIs

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

##Team Members
1. Sagarjit Singh Batish
2. Prikshit Goel
3. Parleen Cheema
