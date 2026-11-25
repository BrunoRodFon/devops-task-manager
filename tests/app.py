
import os
import sqlite3

from flask import Flask, jsonify, request, g, current_app


def get_db():
    if "db" not in g:
        database = current_app.config["DATABASE"]
        g.db = sqlite3.connect(database)
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(exception=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            completed INTEGER NOT NULL DEFAULT 0
        )
    """)

    db.commit()


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        DATABASE=os.environ.get("TASK_MANAGER_DB", "tasks.db")
    )

    if test_config:
        app.config.update(test_config)

    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()

    @app.route("/tasks", methods=["GET"])
    def list_tasks():
        db = get_db()

        tasks = db.execute(
            "SELECT * FROM tasks ORDER BY id"
        ).fetchall()

        result = []

        for task in tasks:
            result.append({
                "id": task["id"],
                "title": task["title"],
                "description": task["description"],
                "completed": bool(task["completed"])
            })

        return jsonify({"tasks": result}), 200

    @app.route("/tasks/<int:task_id>", methods=["GET"])
    def get_task(task_id):
        db = get_db()

        task = db.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()

        if task is None:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({
            "id": task["id"],
            "title": task["title"],
            "description": task["description"],
            "completed": bool(task["completed"])
        }), 200

    @app.route("/tasks", methods=["POST"])
    def create_task():
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON"}), 400

        title = data.get("title")
        description = data.get("description", "")
        completed = data.get("completed", False)

        if not isinstance(title, str) or not title.strip():
            return jsonify({"error": "Title is required"}), 400

        if not isinstance(description, str):
            return jsonify({"error": "Invalid description"}), 400

        if type(completed) is not bool:
            return jsonify({"error": "Invalid completed value"}), 400

        db = get_db()

        cursor = db.execute(
            """
            INSERT INTO tasks (title, description, completed)
            VALUES (?, ?, ?)
            """,
            (title.strip(), description, int(completed))
        )

        db.commit()

        task_id = cursor.lastrowid

        return jsonify({
            "id": task_id,
            "title": title.strip(),
            "description": description,
            "completed": completed
        }), 201

    @app.route("/tasks/<int:task_id>", methods=["PUT"])
    def update_task(task_id):
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON"}), 400

        title = data.get("title")
        description = data.get("description", "")
        completed = data.get("completed", False)

        if not isinstance(title, str) or not title.strip():
            return jsonify({"error": "Title is required"}), 400

        if not isinstance(description, str):
            return jsonify({"error": "Invalid description"}), 400

        if type(completed) is not bool:
            return jsonify({"error": "Invalid completed value"}), 400

        db = get_db()

        cursor = db.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, completed = ?
            WHERE id = ?
            """,
            (title.strip(), description, int(completed), task_id)
        )

        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({
            "id": task_id,
            "title": title.strip(),
            "description": description,
            "completed": completed
        }), 200

    @app.route("/tasks/<int:task_id>", methods=["DELETE"])
    def delete_task(task_id):
        db = get_db()

        cursor = db.execute(
            "DELETE FROM tasks WHERE id = ?", (task_id,)
        )

        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({
            "message": "Task deleted successfully"
        }), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
