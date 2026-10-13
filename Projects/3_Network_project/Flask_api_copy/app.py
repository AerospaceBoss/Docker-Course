from flask import Flask, request, jsonify, render_template_string
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# 🔥 HARDCODED — for dev/learning only
DB_CONFIG = {
    "host": "mysql_container",   # container name on omar_network
    "port": 3306,                # MySQL's internal port (NOT 3307!)
    "user": "root",
    "password": "1234",
    "database": "DockerDB",
}
# Host name in flask container is what lead to the two containers being able to communicate with each other
# Host ip address is answered using the bridge DNS. we can use other container bridge ip instead of the container name but it is not recommended because the ip address can change when the container is restarted


def get_connection():
    """Create a new MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)


# =========================================================
# UI PAGE
# =========================================================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Users UI</title>
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      max-width: 760px;
      margin: 40px auto;
      padding: 0 16px;
      color: #1f2937;
      background: #f9fafb;
    }
    h1 { margin-bottom: 4px; }
    p.subtitle { color: #6b7280; margin-top: 0; margin-bottom: 24px; }
    form {
      display: flex;
      gap: 8px;
      margin: 20px 0;
      flex-wrap: wrap;
    }
    input {
      flex: 1;
      min-width: 160px;
      padding: 10px 12px;
      border: 1px solid #d1d5db;
      border-radius: 8px;
      font-size: 14px;
      outline: none;
      transition: border-color 0.15s;
    }
    input:focus { border-color: #2563eb; }
    button {
      padding: 10px 18px;
      border: none;
      border-radius: 8px;
      background: #2563eb;
      color: white;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.15s;
    }
    button:hover { background: #1d4ed8; }
    button.danger {
      background: #dc2626;
      padding: 6px 12px;
      font-size: 13px;
    }
    button.danger:hover { background: #b91c1c; }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 16px;
      background: white;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    th, td {
      text-align: left;
      padding: 12px;
      border-bottom: 1px solid #f3f4f6;
      font-size: 14px;
    }
    th {
      background: #f9fafb;
      font-weight: 600;
      color: #374151;
    }
    tr:last-child td { border-bottom: none; }
    .msg {
      padding: 12px 16px;
      border-radius: 8px;
      margin: 12px 0;
      font-size: 14px;
    }
    .ok  { background: #dcfce7; color: #166534; }
    .err { background: #fee2e2; color: #991b1b; }
    .empty {
      text-align: center;
      color: #9ca3af;
      padding: 24px;
      font-style: italic;
    }
  </style>
</head>
<body>
  <h1>Users</h1>
  <p class="subtitle">Simple CRUD UI — talks to the Flask API on the same origin.</p>

  <div id="msg"></div>

  <form id="createForm">
    <input id="name"  placeholder="Name"  required autocomplete="off">
    <input id="email" type="email" placeholder="Email" required autocomplete="off">
    <button type="submit">Add User</button>
  </form>

  <table>
    <thead>
      <tr><th>ID</th><th>Name</th><th>Email</th><th></th></tr>
    </thead>
    <tbody id="tbody">
      <tr><td colspan="4" class="empty">Loading…</td></tr>
    </tbody>
  </table>

  <script>
    const API = "";  // same origin as Flask

    function showMsg(text, ok = true) {
      const el = document.getElementById("msg");
      el.innerHTML = `<div class="msg ${ok ? "ok" : "err"}">${text}</div>`;
      setTimeout(() => { el.innerHTML = ""; }, 3000);
    }

    async function loadUsers() {
      const tbody = document.getElementById("tbody");
      try {
        const res = await fetch(`${API}/users`);
        const users = await res.json();

        if (!res.ok) {
          tbody.innerHTML = `<tr><td colspan="4" class="empty">Failed to load: ${users.error || "unknown error"}</td></tr>`;
          return;
        }

        if (users.length === 0) {
          tbody.innerHTML = `<tr><td colspan="4" class="empty">No users yet — add one above.</td></tr>`;
          return;
        }

        tbody.innerHTML = users.map(u => `
          <tr>
            <td>${u.id}</td>
            <td>${escapeHtml(u.name)}</td>
            <td>${escapeHtml(u.email)}</td>
            <td><button class="danger" onclick="deleteUser(${u.id})">Delete</button></td>
          </tr>
        `).join("");
      } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4" class="empty">Network error: ${err.message}</td></tr>`;
      }
    }

    async function deleteUser(id) {
      if (!confirm("Delete this user?")) return;
      const res = await fetch(`${API}/users/${id}`, { method: "DELETE" });
      const data = await res.json();
      if (res.ok) {
        showMsg("User deleted");
        loadUsers();
      } else {
        showMsg(data.error || "Delete failed", false);
      }
    }

    document.getElementById("createForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      const name  = document.getElementById("name").value.trim();
      const email = document.getElementById("email").value.trim();

      const res = await fetch(`${API}/users`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email }),
      });
      const data = await res.json();

      if (res.ok) {
        showMsg(`User "${data.name}" added (id ${data.id})`);
        e.target.reset();
        loadUsers();
      } else {
        showMsg(data.error || "Failed to add user", false);
      }
    });

    function escapeHtml(str) {
      return String(str)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    loadUsers();
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    """Serve the UI."""
    return render_template_string(HTML_PAGE)


# =========================================================
# REST API
# =========================================================

# ---------- POST /users — insert a new user ----------
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    # Validate input
    if not data or "name" not in data or "email" not in data:
        return jsonify({"error": "name and email are required"}), 400

    name = data["name"]
    email = data["email"]

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (name, email),
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({
            "id": new_id,
            "name": name,
            "email": email,
            "message": "User created successfully",
        }), 201

    except Error as e:
        # Duplicate email (UNIQUE constraint)
        if e.errno == 1062:
            return jsonify({"error": "Email already exists"}), 409
        return jsonify({"error": str(e)}), 500


# ---------- GET /users — list all users ----------
@app.route("/users", methods=["GET"])
def list_users():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email FROM users ORDER BY id")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(users), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


# ---------- GET /users/<id> — get one user ----------
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


# ---------- PUT /users/<id> — update a user ----------
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    if not data or ("name" not in data and "email" not in data):
        return jsonify({"error": "name or email required"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Build dynamic UPDATE
        fields, values = [], []
        if "name" in data:
            fields.append("name = %s"); values.append(data["name"])
        if "email" in data:
            fields.append("email = %s"); values.append(data["email"])
        values.append(user_id)

        cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = %s", values)
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()

        if affected == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User updated", "id": user_id}), 200

    except Error as e:
        if e.errno == 1062:
            return jsonify({"error": "Email already exists"}), 409
        return jsonify({"error": str(e)}), 500


# ---------- DELETE /users/<id> — delete a user ----------
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()

        if affected == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User deleted", "id": user_id}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


# ---------- Health check ----------
@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_connection()
        conn.close()
        return jsonify({"status": "ok", "db": "connected"}), 200
    except Error as e:
        return jsonify({"status": "error", "db": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)