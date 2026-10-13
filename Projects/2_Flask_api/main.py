from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage
todos = [
    {"id": 1, "task": "Learn Flask", "done": False},
    {"id": 2, "task": "Build an API", "done": True}
]

# Get all todos
@app.route("/todos", methods=["GET"])
def get_todos():
    return jsonify(todos)

# Get one todo
@app.route("/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    todo = next((t for t in todos if t["id"] == todo_id), None)
    if not todo:
        return jsonify({"error": "Not found"}), 404
    return jsonify(todo)

# Create a todo
@app.route("/todos", methods=["POST"])
def create_todo():
    data = request.get_json()
    if not data or "task" not in data:
        return jsonify({"error": "task is required"}), 400

    todo = {
        "id": max((t["id"] for t in todos), default=0) + 1,
        "task": data["task"],
        "done": data.get("done", False)
    }
    todos.append(todo)
    return jsonify(todo), 201

# Update a todo
@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    todo = next((t for t in todos if t["id"] == todo_id), None)
    if not todo:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()
    todo["task"] = data.get("task", todo["task"])
    todo["done"] = data.get("done", todo["done"])
    return jsonify(todo)

# Delete a todo
@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    global todos
    todo = next((t for t in todos if t["id"] == todo_id), None)
    if not todo:
        return jsonify({"error": "Not found"}), 404

    todos = [t for t in todos if t["id"] != todo_id]
    return jsonify({"message": "Deleted"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)