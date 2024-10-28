import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import date


def initialize_db():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        student_id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        roll_number TEXT NOT NULL,
                        class TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        attendance_id INTEGER PRIMARY KEY,
                        student_id INTEGER,
                        date TEXT NOT NULL,
                        status TEXT NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES students(student_id))''')
    conn.commit()
    conn.close()


initialize_db()


class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Attendance Management System")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f0f0f0")

        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.setup_style()
        self.setup_gui()

    def setup_style(self):
        style = ttk.Style(self.root)
        style.theme_use('clam')

        # Configure styles with centered text
        style.configure("TButton",
                        font=('Arial', 11),
                        background="#4CAF50",
                        foreground="white",
                        padding=10,
                        anchor="center")

        style.configure("TLabel",
                        font=('Arial', 11),
                        background="#f0f0f0",
                        foreground="#2E7D32",
                        anchor="center")

        style.configure("TEntry",
                        font=('Arial', 11),
                        padding=5,
                        anchor="center")

        style.configure("Centered.TEntry",
                        justify="center")

        style.configure("Treeview.Heading",
                        font=('Arial', 11, 'bold'),
                        background="#4CAF50",
                        foreground="white")

        style.configure("Treeview",
                        font=('Arial', 10),
                        rowheight=25)

    def setup_gui(self):
        # Create main container frame
        main_container = ttk.Frame(self.root)
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Configure main container grid
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        # Create and configure notebook
        tab_control = ttk.Notebook(main_container)
        tab_control.grid(row=0, column=0, sticky="nsew")

        # Create tabs
        self.student_tab = ttk.Frame(tab_control)
        self.attendance_tab = ttk.Frame(tab_control)
        self.report_tab = ttk.Frame(tab_control)

        # Configure tab grids
        for tab in (self.student_tab, self.attendance_tab, self.report_tab):
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)

        tab_control.add(self.student_tab, text="Manage Students")
        tab_control.add(self.attendance_tab, text="Mark Attendance")
        tab_control.add(self.report_tab, text="Generate Report")

        self.setup_student_tab()
        self.setup_attendance_tab()
        self.setup_report_tab()

    def setup_student_tab(self):
        # Main container for student tab
        container = ttk.Frame(self.student_tab)
        container.grid(row=0, column=0, sticky="n", padx=20, pady=20)

        # Entry Form Frame
        form_frame = ttk.Frame(container)
        form_frame.grid(row=0, column=0, pady=20)

        # Labels and Entries with center alignment
        labels = ['Name:', 'Roll Number:', 'Class:']
        self.entries = []

        for i, label in enumerate(labels):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky="e")
            entry = ttk.Entry(form_frame, width=30, style="Centered.TEntry")
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.entries.append(entry)

        self.name_entry, self.roll_number_entry, self.class_entry = self.entries

        # Button Frame
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=1, column=0, pady=20)

        # Buttons
        buttons = [
            ("Add Student", self.add_student),
            ("View Students", self.view_students),
            ("Delete Student", self.delete_student)
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(btn_frame, text=text, command=command).grid(row=0, column=i, padx=10)

        # Treeview Frame
        tree_frame = ttk.Frame(container)
        tree_frame.grid(row=2, column=0, pady=20)

        # Treeview with scrollbar
        self.student_tree = ttk.Treeview(tree_frame,
                                         columns=("ID", "Name", "Roll Number", "Class"),
                                         show="headings",
                                         height=10)

        # Configure column widths and headings
        columns = {
            "ID": 100,
            "Name": 200,
            "Roll Number": 150,
            "Class": 150
        }

        for col, width in columns.items():
            self.student_tree.column(col, width=width, anchor="center")
            self.student_tree.heading(col, text=col, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=scrollbar.set)

        self.student_tree.grid(row=0, column=0)
        scrollbar.grid(row=0, column=1, sticky="ns")

    def setup_attendance_tab(self):
        # Main container for attendance tab
        container = ttk.Frame(self.attendance_tab)
        container.grid(row=0, column=0, sticky="n", padx=20, pady=20)

        # Treeview Frame
        tree_frame = ttk.Frame(container)
        tree_frame.grid(row=0, column=0, pady=20)

        self.attendance_tree = ttk.Treeview(tree_frame,
                                            columns=("ID", "Name", "Status"),
                                            show="headings",
                                            height=15)

        # Configure columns
        columns = {
            "ID": 100,
            "Name": 200,
            "Status": 150
        }

        for col, width in columns.items():
            self.attendance_tree.column(col, width=width, anchor="center")
            self.attendance_tree.heading(col, text=col, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=scrollbar.set)

        self.attendance_tree.grid(row=0, column=0)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Button Frame
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=1, column=0, pady=20)

        # Buttons
        buttons = [
            ("Load Students", self.load_students_for_attendance),
            ("Mark Present", self.mark_present),
            ("Mark Absent", self.mark_absent)
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(btn_frame, text=text, command=command).grid(row=0, column=i, padx=10)

    def setup_report_tab(self):
        # Main container for report tab
        container = ttk.Frame(self.report_tab)
        container.grid(row=0, column=0, sticky="n", padx=20, pady=20)

        # Treeview Frame
        tree_frame = ttk.Frame(container)
        tree_frame.grid(row=0, column=0, pady=20)

        self.report_tree = ttk.Treeview(tree_frame,
                                        columns=("Name", "Roll Number", "Date", "Status"),
                                        show="headings",
                                        height=15)

        # Configure columns
        columns = {
            "Name": 200,
            "Roll Number": 150,
            "Date": 150,
            "Status": 100
        }

        for col, width in columns.items():
            self.report_tree.column(col, width=width, anchor="center")
            self.report_tree.heading(col, text=col, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.report_tree.yview)
        self.report_tree.configure(yscrollcommand=scrollbar.set)

        self.report_tree.grid(row=0, column=0)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Generate Report Button
        ttk.Button(container, text="Generate Report", command=self.generate_report).grid(row=1, column=0, pady=20)

    # Database operations methods remain the same
    def add_student(self):
        name = self.name_entry.get()
        roll_number = self.roll_number_entry.get()
        student_class = self.class_entry.get()

        if name and roll_number and student_class:
            conn = sqlite3.connect('attendance.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students (name, roll_number, class) VALUES (?, ?, ?)",
                           (name, roll_number, student_class))
            conn.commit()
            conn.close()

            # Clear entries
            for entry in self.entries:
                entry.delete(0, tk.END)

            messagebox.showinfo("Success", "Student added successfully!")
            self.view_students()
        else:
            messagebox.showerror("Error", "All fields are required!")

    def view_students(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")

        for row in cursor.fetchall():
            self.student_tree.insert("", "end", values=row)

        conn.close()

    def delete_student(self):
        selected = self.student_tree.selection()
        if selected:
            student_id = self.student_tree.item(selected)["values"][0]

            conn = sqlite3.connect('attendance.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE student_id=?", (student_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Student deleted successfully!")
            self.view_students()
        else:
            messagebox.showerror("Error", "Please select a student to delete!")

    def load_students_for_attendance(self):
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, name FROM students")

        for row in cursor.fetchall():
            self.attendance_tree.insert("", "end", values=(row[0], row[1], ""))

        conn.close()

    def mark_present(self):
        selected = self.attendance_tree.selection()
        for item in selected:
            student_id = self.attendance_tree.item(item)["values"][0]
            self.attendance_tree.set(item, column="Status", value="Present")
            self.record_attendance(student_id, "Present")

    def mark_absent(self):
        selected = self.attendance_tree.selection()
        for item in selected:
            student_id = self.attendance_tree.item(item)["values"][0]
            self.attendance_tree.set(item, column="Status", value="Absent")
            self.record_attendance(student_id, "Absent")

    def record_attendance(self, student_id, status):
        today = date.today().strftime("%Y-%m-%d")

        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                       (student_id, today, status))
        conn.commit()
        conn.close()

    def generate_report(self):
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)

        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT s.name, s.roll_number, a.date, a.status 
                         FROM attendance a 
                         JOIN students s ON a.student_id = s.student_id
                         ORDER BY a.date DESC''')

        for row in cursor.fetchall():
            self.report_tree.insert("", "end", values=row)

        conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
