# CampusConnect: Integration and Testing

This file covers the integration and testing work: how the JavaScript frontend connects to the FastAPI backend, and how everything was tested.

## 1. How the integration works

All frontend code that talks to the backend is in one file, `script.js`.

- The backend address is set once at the top: `const API = "http://127.0.0.1:8000";`
- After login, the token returned by `/login` is saved in the browser (`localStorage`).
- Every later request sends that token as `Authorization: Bearer <token>`.
- If the token is missing or expired, the user is sent back to `login.html`.
- CORS is enabled in `main.py`, so the frontend (port 5500) can call the backend (port 8000).

### Which page calls which API

| Page | What the user does | API called |
|---|---|---|
| `register.html` | Create account | `POST /register` |
| `login.html` | Log in | `POST /login` |
| `dashboard.html` | See all issues | `GET /issues` |
| `create-issue.html` | Load category list | `GET /categories` |
| `create-issue.html` | Submit a new issue | `POST /issues` |
| `6_issue_detail_page.html` | View one issue | `GET /issues/{id}` |
| `6_issue_detail_page.html` | Change status | `PUT /issues/{id}/status` |

## 2. Bugs found and fixed during integration

| Problem | Fix |
|---|---|
| `GET /issues` crashed (typo `ORDER BY issues.id D ESC` in `main.py`) | Changed to `DESC` |
| Login button only redirected, it never checked the password | Login now calls `/login` and stores the token |
| Dashboard showed 2 hardcoded fake issues | Dashboard now loads real issues from the database |
| Register page had no script and no `<html>` structure | Added the structure and the register code |
| Issue form had a "General" category the backend rejects | Categories now load from `/categories`; HTML options match the backend |
| Issue detail page was only plain text | Built the page with status dropdown and Update button |
| User text could be inserted as HTML | Text is escaped before it is shown |

## 3. How to run everything

Open two terminals in the project folder (the one with `main.py`).

**Terminal 1: backend**
```
pip install -r requirements.txt
python -m uvicorn main:app --reload
```
Check that http://127.0.0.1:8000/docs opens.

**Terminal 2: frontend**
```
python -m http.server 5500
```
Open http://127.0.0.1:5500/login.html

Do not double-click the HTML files. Opening them as `file://` can cause CORS errors.

## 4. Test plan and results

Tick each box after testing with the real backend running.

### Registration and login
- [ ] Register a new account, then you are taken to the login page
- [ ] Register with the same email again, then "Email already registered" is shown
- [ ] Register with a password shorter than 6 characters, then an error is shown
- [ ] Log in with a wrong password, then "Wrong email or password" is shown
- [ ] Log in with the correct details, then the dashboard opens
- [ ] Open `dashboard.html` without logging in, then you are sent to login
- [ ] Click Logout, then the token is cleared and you can't open the dashboard

### Issues
- [ ] Dashboard with no issues shows "No issues reported yet"
- [ ] Submit an issue, then it appears on the dashboard
- [ ] Refresh the page, then the issue is still there (saved in the database)
- [ ] Newest issue is shown first
- [ ] Category list shows: Classroom, Campus, Lost & Found, Library, Lab, Other
- [ ] Submit with an empty title or description, then the form blocks it
- [ ] Title longer than 100 or description longer than 1000 characters is blocked

### Status updates
- [ ] Open an issue, change status to "In Progress", click Update, then the badge changes
- [ ] Refresh, then the new status is still there
- [ ] Dashboard shows the new status
- [ ] Set status to "Resolved" and check it again

### Other checks
- [ ] Stop the backend, reload the dashboard, then "Cannot reach the server" is shown
- [ ] Type `<b>test</b>` as a title, then it shows as plain text (not bold)
- [ ] Open the SQLite file (`campusconnect.db`) and confirm the rows were saved
- [ ] F12 Console shows no red errors on any page

### Results already verified
The frontend was tested in a real browser (Chromium) against a copy of the API rules from `main.py`. 18 of 18 checks passed: redirect when logged out, wrong and correct login, register, empty dashboard, category list, submit issue, issue shown on dashboard, HTML escaping, issue detail, status update and refresh, backend-down message, bad token, logout, and no JavaScript errors.
The real FastAPI server was not part of that run, so the checklist above should be ticked once on the real backend.

## 5. Common errors and what they mean

| What you see | Cause | Fix |
|---|---|---|
| "Cannot reach the server" | Backend is not running | Start `uvicorn` |
| CORS error in the Console | HTML opened as a file, or CORS missing | Use `http.server` or Live Server; keep the CORS block in `main.py` |
| 401 in the Network tab | Not logged in or token expired | Log in again |
| 422 | Data sent does not match what the API expects | Compare with http://127.0.0.1:8000/docs |
| 500 | Backend crashed | Read the error in the uvicorn terminal |
| 404 | Wrong URL or issue id | Check the route spelling |

## 6. Known gaps
- `profile.html` does not exist yet, so the Profile link in the menu leads nowhere.
- Most pages have very little CSS. `style.css` only styles text boxes, while `2_style.css` has the full styles.
- Any logged-in user can change the status of any issue (the backend has no admin role).

## Team
Integration and Testing: Parleen Cheema
