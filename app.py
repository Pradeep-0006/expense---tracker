from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


# Create database
def init_db():
    conn = sqlite3.connect("expenses.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)

    conn.close()


# Home page
@app.route("/")
def home():

    conn = sqlite3.connect("expenses.db")

    expenses = conn.execute("""
        SELECT * FROM expenses
        ORDER BY id DESC
    """).fetchall()

    total_expenses = conn.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
    """).fetchone()[0]

    transaction_count = conn.execute("""
        SELECT COUNT(*)
        FROM expenses
    """).fetchone()[0]

    from datetime import date
    today = date.today().isoformat()

    today_expenses = conn.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE date = ?
    """, (today,)).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        expenses=expenses,
        total_expenses=total_expenses,
        today_expenses=today_expenses,
        transaction_count=transaction_count
    )


# Add expense
@app.route("/add", methods=["POST"])
def add_expense():

    description = request.form["description"]
    amount = request.form["amount"]
    category = request.form["category"]
    date = request.form["date"]

    conn = sqlite3.connect("expenses.db")

    conn.execute("""
        INSERT INTO expenses
        (description, amount, category, date)
        VALUES (?, ?, ?, ?)
    """, (description, amount, category, date))

    conn.commit()
    conn.close()

    return redirect("/")


# Edit expense
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_expense(id):

    conn = sqlite3.connect("expenses.db")

    if request.method == "POST":

        description = request.form["description"]
        amount = request.form["amount"]
        category = request.form["category"]
        date = request.form["date"]

        conn.execute("""
            UPDATE expenses
            SET description = ?,
                amount = ?,
                category = ?,
                date = ?
            WHERE id = ?
        """, (description, amount, category, date, id))

        conn.commit()
        conn.close()

        return redirect("/")

    expense = conn.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit.html",
        expense=expense
    )


# Delete expense
@app.route("/delete/<int:id>")
def delete_expense(id):

    conn = sqlite3.connect("expenses.db")

    conn.execute(
        "DELETE FROM expenses WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# Reports page
@app.route("/reports")
def reports():

    conn = sqlite3.connect("expenses.db")

    total_expenses = conn.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
    """).fetchone()[0]

    category_data = conn.execute("""
        SELECT category, COALESCE(SUM(amount), 0)
        FROM expenses
        GROUP BY category
    """).fetchall()

    conn.close()

    category_totals = {}

    for category, amount in category_data:
        category_totals[category] = amount

    return render_template(
        "reports.html",
        total_expenses=total_expenses,
        category_totals=category_totals
    )


# Monthly Reports
@app.route("/monthly-reports")
def monthly_reports():

    conn = sqlite3.connect("expenses.db")

    monthly_data = conn.execute("""
        SELECT
            strftime('%Y-%m', date) AS month,
            SUM(amount)
        FROM expenses
        GROUP BY month
        ORDER BY month DESC
    """).fetchall()

    conn.close()

    return render_template(
        "monthly_reports.html",
        monthly_data=monthly_data
    )

# Yearly Reports
@app.route("/yearly-reports")
def yearly_reports():

    conn = sqlite3.connect("expenses.db")

    yearly_data = conn.execute("""
        SELECT
            strftime('%Y', date) AS year,
            SUM(amount)
        FROM expenses
        GROUP BY year
        ORDER BY year DESC
    """).fetchall()

    conn.close()

    return render_template(
        "yearly_reports.html",
        yearly_data=yearly_data
    )
# Initialize database when application starts
init_db()

# Start Flask application
if __name__ == "__main__":
    app.run(debug=False)

