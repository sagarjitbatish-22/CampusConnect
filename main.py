"""CampusConnect backend - FastAPI + SQLite.

Run:  uvicorn main:app --reload
Docs: http://127.0.0.1:8000/docs  (test every API here)
"""
import hashlib
import secrets
import sqlite3
from typing import Literal, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH = "campusconnect.db"

CATEGORIES = [
    "Classroom", "Campus", "Lost & Found", "Library", "Lab", "Other",
]

app = FastAPI(title="CampusConnect API")

# Lets the HTML/JS frontend (opened from another port/file) call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Database ----------
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt          TEXT NOT NULL,
            created_at    TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS issues (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            description TEXT NOT NULL,
            category    TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'Open',
            created_by  INTEGER NOT NULL,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token   TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )
    conn.commit()
    conn.close()


init_db()


# ---------- Helpers ----------
def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 100_000
    ).hex()


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: sqlite3.Connection = Depends(get_db),
):
    """Reads 'Authorization: Bearer <token>' and returns the logged-in user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Please log in first")
    token = authorization.split(" ", 1)[1]
    user = db.execute(
        """SELECT users.id, users.name, users.email, users.created_at
           FROM sessions JOIN users ON users.id = sessions.user_id
           WHERE sessions.token = ?""",
        (token,),
    ).fetchone()
    if not user:
        raise HTTPException(401, "Invalid or expired token")
    return user


# ---------- Request models ----------
class RegisterIn(BaseModel):
    name: str = Field(min_length=1)
    email: str = Field(min_length=3)
    password: str = Field(min_length=6)


class LoginIn(BaseModel):
    email: str
    password: str


class IssueIn(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=1000)
    category: str


class StatusIn(BaseModel):
    status: Literal["Open", "In Progress", "Resolved"]


# ---------- Auth APIs ----------
@app.post("/register", status_code=201)
def register(data: RegisterIn, db: sqlite3.Connection = Depends(get_db)):
    email = data.email.strip().lower()
    if db.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
        raise HTTPException(400, "Email already registered")
    salt = secrets.token_hex(16)
    db.execute(
        "INSERT INTO users (name, email, password_hash, salt) VALUES (?, ?, ?, ?)",
        (data.name.strip(), email, hash_password(data.password, salt), salt),
    )
    db.commit()
    return {"message": "Registered successfully"}


@app.post("/login")
def login(data: LoginIn, db: sqlite3.Connection = Depends(get_db)):
    email = data.email.strip().lower()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not user or user["password_hash"] != hash_password(data.password, user["salt"]):
        raise HTTPException(401, "Wrong email or password")
    token = secrets.token_hex(32)
    db.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user["id"]))
    db.commit()
    return {"token": token, "name": user["name"]}


@app.get("/me")
def profile(user=Depends(get_current_user)):
    """Simple profile page data."""
    return dict(user)


# ---------- Issue APIs ----------
@app.get("/categories")
def categories():
    return CATEGORIES


@app.post("/issues", status_code=201)
def create_issue(
    data: IssueIn,
    user=Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    if data.category not in CATEGORIES:
        raise HTTPException(400, f"Category must be one of {CATEGORIES}")
    cur = db.execute(
        "INSERT INTO issues (title, description, category, created_by) VALUES (?, ?, ?, ?)",
        (data.title.strip(), data.description.strip(), data.category, user["id"]),
    )
    db.commit()
    return {"message": "Issue created", "id": cur.lastrowid}


ISSUE_SELECT = """
    SELECT issues.id, issues.title, issues.description, issues.category,
           issues.status, issues.created_at, users.name AS created_by
    FROM issues JOIN users ON users.id = issues.created_by
"""


@app.get("/issues")
def get_issues(
    status: Optional[str] = None,
    category: Optional[str] = None,
    user=Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    """List all issues (dashboard). Optional filters: ?status=Open&category=Classroom"""
    query, params = ISSUE_SELECT + " WHERE 1=1", []
    if status:
        query += " AND issues.status = ?"
        params.append(status)
    if category:
        query += " AND issues.category = ?"
        params.append(category)
    query += " ORDER BY issues.id DESC"
    return [dict(r) for r in db.execute(query, params).fetchall()]


@app.get("/issues/{issue_id}")
def get_issue(
    issue_id: int,
    user=Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    row = db.execute(ISSUE_SELECT + " WHERE issues.id = ?", (issue_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Issue not found")
    return dict(row)


@app.put("/issues/{issue_id}/status")
def update_status(
    issue_id: int,
    data: StatusIn,
    user=Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    cur = db.execute("UPDATE issues SET status = ? WHERE id = ?", (data.status, issue_id))
    db.commit()
    if cur.rowcount == 0:
        raise HTTPException(404, "Issue not found")
    return {"message": "Status updated", "status": data.status}
