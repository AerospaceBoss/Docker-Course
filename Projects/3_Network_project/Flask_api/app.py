from flask import Flask, request, jsonify
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
# Host ip address is answered using the bridge DnS . we can use other container bridge ip instead of the container name but it is not recommended because the ip address can change when the container is restarted
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ... rest of your endpoints unchanged
def get_connection():
    """Create a new MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)

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