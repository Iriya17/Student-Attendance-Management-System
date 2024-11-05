import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import date

def initialize_db():
    """Initializes the SQLite database and creates necessary tables."""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        roll_number TEXT NOT NULL,
                        class TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        self.root.geometry("800x600")
        self.root.configure(bg='#C6E7FF')

        self.setup_style()
        self.setup_gui()
        self.view_students()

    def setup_style(self):
        """Sets the style for the application."""
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure("TButton", font=('Arial', 11, 'bold'),  foreground="White", background="Black", padding=10)
        style.configure("TLabel", font=('Arial', 11),  foreground="Black")
        style.configure("TEntry", font=('Arial', 11), padding=5)
        style.configure("Treeview.Heading", font=('Arial', 11, 'bold'), background="#D4F6FF", foreground="Black")
        style.configure("Treeview", font=('Arial', 10), rowheight=25)

    def setup_gui(self):
        """Sets up the main GUI components."""        
        main_container = ttk.Frame(self.root)
        main_container.pack(expand=True)

        tab_control = ttk.Notebook(main_container)
        tab_control.pack(expand=True, fill='both')

        # Create tabs
        self.student_tab = ttk.Frame(tab_control)
        self.attendance_tab = ttk.Frame(tab_control)
        self.report_tab = ttk.Frame(tab_control)

        tab_control.add(self.student_tab, text="Manage Students")
        tab_control.add(self.attendance_tab, text="Mark Attendance")
        tab_control.add(self.report_tab, text="Generate Report")

        self.setup_student_tab()
        self.setup_attendance_tab()
        self.setup_report_tab()

    def setup_student_tab(self):
        """Sets up the GUI components for the Student Management tab."""        
        container = ttk.Frame(self.student_tab)
        container.pack(expand=True)

        form_frame = ttk.Frame(container)
        form_frame.pack(pady=20)

        # Labels and Entries
        labels = ['Name:', 'Roll Number:', 'Class:']
        self.entries = []

        for i, label in enumerate(labels):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky="e")
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.entries.append(entry)

        self.name_entry, self.roll_number_entry, self.class_entry = self.entries

        # Button Frame
        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=20)

        buttons = [
            ("Add Student", self.add_student),
            ("View Students", self.view_students),
            ("Delete Student", self.delete_student)
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(btn_frame, text=text, command=command).grid(row=0, column=i, padx=10)

        # Treeview Frame
        self.student_tree = self.create_treeview(container, 
                                                  ["ID", "Name", "Roll Number", "Class"],
                                                  ["100", "200", "150", "150"])

    def setup_attendance_tab(self):
        """Sets up the GUI components for the Attendance tab."""        
        container = ttk.Frame(self.attendance_tab)
        container.pack(expand=True)

        # Treeview Frame
        self.attendance_tree = self.create_treeview(container, 
                                                     ["ID", "Name", "Status"],
                                                     ["100", "200", "150"])

        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=20)

        buttons = [
            ("Load Students", self.load_students_for_attendance),
            ("Mark Present", self.mark_present),
            ("Mark Absent", self.mark_absent)
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(btn_frame, text=text, command=command).grid(row=0, column=i, padx=10)

    def setup_report_tab(self):
        """Sets up the GUI components for the Report tab."""        
        container = ttk.Frame(self.report_tab)
        container.pack(expand=True)

        self.report_tree = self.create_treeview(container, 
                                                 ["Name", "Roll Number", "Date", "Status"],
                                                 ["200", "150", "150", "100"])

        ttk.Button(container, text="Generate Report", command=self.generate_report).pack(pady=20)

    def create_treeview(self, parent, columns, widths):
        """Creates a Treeview with specified columns and widths."""        
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(pady=20)

        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        for col, width in zip(columns, widths):
            tree.column(col, width=int(width), anchor="center")
            tree.heading(col, text=col, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        return tree

    def execute_db_query(self, query, params=(), fetch=False):
        """Executes a database query and handles errors."""        
        try:
            conn = sqlite3.connect('attendance.db')
            cursor = conn.cursor()
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    def add_student(self):
        """Adds a new student to the database."""        
        name = self.name_entry.get()
        roll_number = self.roll_number_entry.get()
        student_class = self.class_entry.get()

        if name and roll_number and student_class:
            self.execute_db_query("INSERT INTO students (name, roll_number, class) VALUES (?, ?, ?)", 
                                   (name, roll_number, student_class))
            messagebox.showinfo("Success", "Student added successfully!")
            self.view_students()
        else:
            messagebox.showwarning("Input Error", "Please fill all fields.")

    def view_students(self):
        """Displays all students in the Treeview."""        
        for row in self.student_tree.get_children():
            self.student_tree.delete(row)

        students = self.execute_db_query("SELECT * FROM students", fetch=True)
        for student in students:
            self.student_tree.insert("", "end", values=student)

    def delete_student(self):
        """Deletes the selected student from the database."""        
        selected_item = self.student_tree.selection()
        if selected_item:
            student_id = self.student_tree.item(selected_item)["values"][0]
            self.execute_db_query("DELETE FROM students WHERE student_id=?", (student_id,))
            messagebox.showinfo("Success", "Student deleted successfully!")
            self.view_students()
        else:
            messagebox.showwarning("Selection Error", "Please select a student to delete.")

    def load_students_for_attendance(self):
        """Loads students into the attendance Treeview."""        
        for row in self.attendance_tree.get_children():
            self.attendance_tree.delete(row)

        students = self.execute_db_query("SELECT * FROM students", fetch=True)
        for student in students:
            self.attendance_tree.insert("", "end", values=(student[0], student[1], "Pending"))

    def mark_present(self):
        """Marks the selected student as present."""        
        self.mark_attendance("Present")

    def mark_absent(self):
        """Marks the selected student as absent."""        
        self.mark_attendance("Absent")

    def mark_attendance(self, status):
        """Marks the selected student in the attendance Treeview."""        
        selected_item = self.attendance_tree.selection()
        if selected_item:
            student_id = self.attendance_tree.item(selected_item)["values"][0]
            current_date = date.today().isoformat()
            self.execute_db_query("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                                   (student_id, current_date, status))

            # Update the Treeview to show the marked status
            self.attendance_tree.item(selected_item, values=(student_id, self.attendance_tree.item(selected_item)["values"][1], status))
            
            messagebox.showinfo("Success", f"Marked as {status.lower()}!")
        else:
            messagebox.showwarning("Selection Error", "Please select a student to mark.")

    def generate_report(self):
        """Generates a report of attendance."""        
        for row in self.report_tree.get_children():
            self.report_tree.delete(row)

        report_data = self.execute_db_query('''SELECT students.name, students.roll_number, attendance.date, attendance.status
                                                FROM attendance
                                                JOIN students ON attendance.student_id = students.student_id''', fetch=True)

        for report in report_data:
            self.report_tree.insert("", "end", values=report)

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()

