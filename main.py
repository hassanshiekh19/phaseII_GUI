import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_FILE = "students.db"


# ────────────────────────────────────────────────────────
# DATABASE HELPERS
# ────────────────────────────────────────────────────────
def init_db():
    """Create the table once if it doesn’t exist."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS students (
                   id       INTEGER PRIMARY KEY AUTOINCREMENT,
                   name     TEXT   NOT NULL,
                   math     REAL   NOT NULL,
                   english  REAL   NOT NULL,
                   science  REAL   NOT NULL,
                   total    REAL   NOT NULL,
                   average  REAL   NOT NULL,
                   grade    TEXT   NOT NULL
            )"""
        )
        conn.commit()


def add_student(rec):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "INSERT INTO students(name, math, english, science, total, average, grade) "
            "VALUES (?,?,?,?,?,?,?)",
            (
                rec["Name"],
                rec["Math"],
                rec["English"],
                rec["Science"],
                rec["Total"],
                rec["Average"],
                rec["Grade"],
            ),
        )
        conn.commit()


def search_students(name_like=""):
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        if name_like.strip():
            cur.execute(
                "SELECT name, math, english, science, total, average, grade "
                "FROM students WHERE name LIKE ?",
                (f"%{name_like.strip()}%",),
            )
        else:  # return all
            cur.execute(
                "SELECT name, math, english, science, total, average, grade FROM students"
            )
        return cur.fetchall()


# ────────────────────────────────────────────────────────
# GRADE CALCULATION
# ────────────────────────────────────────────────────────
def calculate_grade(avg):
    return "A" if avg >= 85 else "B" if avg >= 70 else "C" if avg >= 50 else "F"


# ────────────────────────────────────────────────────────
# GUI CALLBACKS
# ────────────────────────────────────────────────────────
def submit():
    try:
        name = name_entry.get().strip()
        math = float(math_entry.get())
        english = float(english_entry.get())
        science = float(science_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Enter valid numbers for marks.")
        return
    if not name:
        messagebox.showerror("Input Error", "Student name is required.")
        return

    total = math + english + science
    average = round(total / 3, 2)
    grade = calculate_grade(average)

    record = {
        "Name": name,
        "Math": math,
        "English": english,
        "Science": science,
        "Total": total,
        "Average": average,
        "Grade": grade,
    }
    add_student(record)
    populate_table(search_students())  # refresh full list
    clear_inputs()


def clear_inputs():
    for ent in (name_entry, math_entry, english_entry, science_entry):
        ent.delete(0, tk.END)


def do_search():
    term = search_entry.get()
    results = search_students(term)
    populate_table(results)


def populate_table(rows):
    # clear existing
    for r in results_tv.get_children():
        results_tv.delete(r)
    # insert new rows
    for row in rows:
        results_tv.insert("", tk.END, values=row)


# ────────────────────────────────────────────────────────
# BUILD GUI
# ────────────────────────────────────────────────────────
def build_gui():
    root = tk.Tk()
    root.title("Student Result Recording System")
    root.geometry("800x550")

    # Input frame
    frm_input = ttk.LabelFrame(root, text="Add Student")
    frm_input.pack(fill="x", padx=10, pady=8)

    ttk.Label(frm_input, text="Name").grid(row=0, column=0, padx=5, pady=4, sticky="w")
    ttk.Label(frm_input, text="Math").grid(row=0, column=2, padx=5, pady=4, sticky="w")
    ttk.Label(frm_input, text="English").grid(
        row=0, column=4, padx=5, pady=4, sticky="w"
    )
    ttk.Label(frm_input, text="Science").grid(
        row=0, column=6, padx=5, pady=4, sticky="w"
    )

    global name_entry, math_entry, english_entry, science_entry
    name_entry = ttk.Entry(frm_input, width=18)
    math_entry = ttk.Entry(frm_input, width=10)
    english_entry = ttk.Entry(frm_input, width=10)
    science_entry = ttk.Entry(frm_input, width=10)

    name_entry.grid(row=0, column=1, padx=5, pady=4)
    math_entry.grid(row=0, column=3, padx=5, pady=4)
    english_entry.grid(row=0, column=5, padx=5, pady=4)
    science_entry.grid(row=0, column=7, padx=5, pady=4)

    ttk.Button(frm_input, text="Save", command=submit).grid(
        row=0, column=8, padx=10, pady=4
    )

    # Search frame
    frm_search = ttk.LabelFrame(root, text="Search")
    frm_search.pack(fill="x", padx=10, pady=4)

    ttk.Label(frm_search, text="Student Name (partial or full)").grid(
        row=0, column=0, padx=5, pady=4
    )
    global search_entry
    search_entry = ttk.Entry(frm_search, width=30)
    search_entry.grid(row=0, column=1, padx=5, pady=4)
    ttk.Button(frm_search, text="Search", command=do_search).grid(
        row=0, column=2, padx=5, pady=4
    )
    ttk.Button(frm_search, text="Show All", command=lambda: populate_table(search_students())).grid(
        row=0, column=3, padx=5, pady=4
    )

    # Results table
    frm_table = ttk.Frame(root)
    frm_table.pack(fill="both", expand=True, padx=10, pady=6)

    cols = ("Name", "Math", "English", "Science", "Total", "Average", "Grade")
    global results_tv
    results_tv = ttk.Treeview(frm_table, columns=cols, show="headings", height=15)
    for col in cols:
        results_tv.heading(col, text=col)
        results_tv.column(col, anchor="center")
    results_tv.pack(side="left", fill="both", expand=True)

    # scrollbar
    scroll_y = ttk.Scrollbar(frm_table, orient="vertical", command=results_tv.yview)
    results_tv.configure(yscroll=scroll_y.set)
    scroll_y.pack(side="right", fill="y")

    # populate once at start
    populate_table(search_students())
    return root


# ────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app = build_gui()
    app.mainloop()
