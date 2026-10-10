// CampusConnect frontend <-> FastAPI connection
// One file used by every page. Each block below only runs if its page has the matching element.

const API = "http://127.0.0.1:8000";

// ---------- Helpers ----------
function getToken() {
    return localStorage.getItem("token");
}

// Sends the user to the login page if they are not logged in
function requireLogin() {
    if (!getToken()) {
        window.location.href = "login.html";
        return false;
    }
    return true;
}

// Turns FastAPI error replies into a readable message
function errorText(data) {
    if (!data || !data.detail) return "";
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
        return data.detail
            .map((d) => (d.loc ? d.loc[d.loc.length - 1] + ": " : "") + d.msg)
            .join("\n");
    }
    return "";
}

// Calls the backend. Adds the login token automatically.
async function api(path, options = {}) {
    const headers = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) headers["Authorization"] = "Bearer " + token;

    let res;
    try {
        res = await fetch(API + path, { ...options, headers });
    } catch (err) {
        throw new Error("Cannot reach the server. Is the backend running at " + API + " ?");
    }

    // Expired / missing token: back to login (but not when the login itself failed)
    if (res.status === 401 && path !== "/login") {
        localStorage.removeItem("token");
        localStorage.removeItem("name");
        window.location.href = "login.html";
        throw new Error("Please log in again.");
    }

    let data = null;
    try {
        data = await res.json();
    } catch (err) {
        // reply had no JSON body
    }

    if (!res.ok) {
        throw new Error(errorText(data) || "Request failed (" + res.status + ")");
    }
    return data;
}

// Stops user-typed text from being run as HTML
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text == null ? "" : String(text);
    return div.innerHTML;
}

function statusClass(status) {
    if (status === "In Progress") return "progress";
    if (status === "Resolved") return "resolved";
    return "open";
}

// ---------- Login page ----------
const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        try {
            const data = await api("/login", {
                method: "POST",
                body: JSON.stringify({
                    email: document.getElementById("email").value,
                    password: document.getElementById("password").value,
                }),
            });
            localStorage.setItem("token", data.token);
            localStorage.setItem("name", data.name);
            window.location.href = "dashboard.html";
        } catch (err) {
            alert(err.message);
        }
    });
}

// ---------- Register page ----------
const registerForm = document.getElementById("registerForm");

if (registerForm) {
    registerForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        try {
            await api("/register", {
                method: "POST",
                body: JSON.stringify({
                    name: document.getElementById("name").value,
                    email: document.getElementById("registerEmail").value,
                    password: document.getElementById("registerPassword").value,
                }),
            });
            alert("Account created! Please log in.");
            window.location.href = "login.html";
        } catch (err) {
            alert(err.message);
        }
    });
}

// ---------- Logout link (dashboard) ----------
const logoutLink = document.getElementById("logoutLink");

if (logoutLink) {
    logoutLink.addEventListener("click", function () {
        localStorage.removeItem("token");
        localStorage.removeItem("name");
    });
}

// ---------- Dashboard: show real issues ----------
const issuesContainer = document.getElementById("issuesContainer");

async function loadIssues() {
    if (!requireLogin()) return;
    issuesContainer.innerHTML = "<p>Loading issues...</p>";
    try {
        const issues = await api("/issues");
        if (issues.length === 0) {
            issuesContainer.innerHTML = "<p>No issues reported yet.</p>";
            return;
        }
        issuesContainer.innerHTML = issues
            .map(
                (i) => `
            <div class="issue-card">
                <h3><a href="6_issue_detail_page.html?id=${Number(i.id)}">${escapeHtml(i.title)}</a></h3>
                <p>${escapeHtml(i.description)}</p>
                <span class="category">${escapeHtml(i.category)}</span>
                <span class="status ${statusClass(i.status)}">${escapeHtml(i.status)}</span>
            </div>`
            )
            .join("");
    } catch (err) {
        issuesContainer.innerHTML = "<p>" + escapeHtml(err.message) + "</p>";
    }
}

if (issuesContainer) {
    loadIssues();
}

// ---------- Create issue page ----------
const issueForm = document.getElementById("issueForm");

async function loadCategories() {
    const select = document.getElementById("category");
    try {
        const categories = await api("/categories");
        select.innerHTML =
            '<option value="">Select Category</option>' +
            categories
                .map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`)
                .join("");
    } catch (err) {
        // keep the options already written in the HTML
    }
}

if (issueForm) {
    if (requireLogin()) {
        loadCategories();
    }

    issueForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        try {
            await api("/issues", {
                method: "POST",
                body: JSON.stringify({
                    title: document.getElementById("title").value.trim(),
                    description: document.getElementById("description").value.trim(),
                    category: document.getElementById("category").value,
                }),
            });
            alert("Issue submitted!");
            window.location.href = "dashboard.html";
        } catch (err) {
            alert(err.message);
        }
    });
}

// ---------- Issue detail page: view issue + update status ----------
const issueDetail = document.getElementById("issueDetail");

async function loadIssueDetail() {
    if (!requireLogin()) return;
    const id = new URLSearchParams(window.location.search).get("id");
    if (!id) {
        issueDetail.innerHTML = "<p>No issue selected. Go back to the dashboard.</p>";
        return;
    }
    try {
        const issue = await api("/issues/" + encodeURIComponent(id));
        document.getElementById("issueTitle").textContent = issue.title;
        document.getElementById("issueCategory").textContent = issue.category;
        const statusBadge = document.getElementById("issueStatus");
        statusBadge.textContent = issue.status;
        statusBadge.className = "status " + statusClass(issue.status);
        document.getElementById("issueDescription").textContent = issue.description;
        document.getElementById("issueBy").textContent = issue.created_by;
        document.getElementById("issueDate").textContent = issue.created_at;
        document.getElementById("statusSelect").value = issue.status;
    } catch (err) {
        issueDetail.innerHTML = "<p>" + escapeHtml(err.message) + "</p>";
    }
}

if (issueDetail) {
    loadIssueDetail();

    document.getElementById("updateStatusBtn").addEventListener("click", async function () {
        const id = new URLSearchParams(window.location.search).get("id");
        try {
            await api("/issues/" + encodeURIComponent(id) + "/status", {
                method: "PUT",
                body: JSON.stringify({ status: document.getElementById("statusSelect").value }),
            });
            alert("Status updated!");
            loadIssueDetail();
        } catch (err) {
            alert(err.message);
        }
    });
}
