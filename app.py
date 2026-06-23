from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import csv

app = Flask(__name__)

def create_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        phone TEXT UNIQUE
    )
    """)

    conn.commit()
    conn.close()

create_database()


@app.route("/", methods=["GET", "POST"])
def home():

    message = ""

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? OR phone=?",
            (email, phone)
        )

        duplicate = cursor.fetchone()

        if duplicate:
            message = "❌ Duplicate Data Found!"
        else:
            cursor.execute(
                "INSERT INTO users(name,email,phone) VALUES(?,?,?)",
                (name, email, phone)
            )
            conn.commit()
            message = "✅ Data Added Successfully"

        conn.close()

    search = request.args.get("search", "")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if search:
        cursor.execute(
            "SELECT * FROM users WHERE name LIKE ? OR email LIKE ?",
            (f"%{search}%", f"%{search}%")
        )
    else:
        cursor.execute("SELECT * FROM users")

    records = cursor.fetchall()
    conn.close()

    return render_template(
        "index.html",
        records=records,
        message=message,
        search=search
    )


@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()

    conn.close()

    return redirect("/")


@app.route("/export")
def export():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()

    conn.close()

    with open("users.csv", "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["ID", "Name", "Email", "Phone"])

        for row in data:
            writer.writerow(row)

    return send_file(
        "users.csv",
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)