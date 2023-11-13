import tkinter as tk
from tkinter import ttk, simpledialog

class StudentFormDialog(simpledialog.Dialog):
    def __init__(self, master, title, classrooms, id=None, first_name="", last_name="", classroom_id=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.default_classroom = next(filter(lambda item: item.id == classroom_id, classrooms), None)
        self.classrooms = classrooms
        # list(map(lambda obj: (obj.id, obj.name), classrooms))

        super().__init__(master, title)

    def body(self, master):
        tk.Label(master, text="First Name:").grid(row=0, sticky="w")
        tk.Label(master, text="Last Name:").grid(row=1, sticky="w")
        tk.Label(master, text="Classroom:").grid(row=2, sticky="w")

        self.first_name_entry = tk.Entry(master, width=20)
        self.last_name_entry = tk.Entry(master, width=20)

        # Get the displayed texts from classrooms
        classrooms_text = [item.name for item in self.classrooms]

        self.classroom_var = tk.StringVar(master)
        self.classroom_var.set(self.default_classroom.name if self.default_classroom else classrooms_text[0])

        self.classroom_dropdown = tk.OptionMenu(master, self.classroom_var, *classrooms_text)
        self.classroom_dropdown.config(width=16)

        self.first_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.last_name_entry.grid(row=1, column=1, padx=5, pady=5)
        self.classroom_dropdown.grid(row=2, column=1, padx=5, pady=5)

        # Set default values if provided
        self.first_name_entry.insert(0, self.first_name)
        self.last_name_entry.insert(0, self.last_name)

        return self.first_name_entry

    def apply(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()

        # Get the selected classroom tuple
        classroom = next((item for item in self.classrooms if item.name == self.classroom_var.get()), None)

        self.result = {'first_name': first_name, 'last_name': last_name, 'classroom': classroom}

        if self.id:
            self.result['id'] = self.id 

class TeacherFormDialog(simpledialog.Dialog):
    def __init__(self, master, title, classrooms, id=None, first_name="", last_name="", assigned_classrooms=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.assigned_classrooms = assigned_classrooms if assigned_classrooms else []
        self.classrooms = classrooms

        super().__init__(master, title)

    def body(self, master):
        tk.Label(master, text="First Name:").grid(row=0, sticky="w")
        tk.Label(master, text="Last Name:").grid(row=1, sticky="w")
        tk.Label(master, text="Classrooms:").grid(row=2, sticky="w")

        self.first_name_entry = tk.Entry(master, width=20)
        self.last_name_entry = tk.Entry(master, width=20)

        self.classroom_checkboxes = []

        for i, classroom in enumerate(self.classrooms):
            print('assigned_classrooms', self.assigned_classrooms, classroom.id)
            var = tk.IntVar(value=classroom.id in self.assigned_classrooms)
            checkbox = tk.Checkbutton(master, text=classroom.name, variable=var)
            checkbox.grid(row=i + 2, column=1, sticky="w")
            self.classroom_checkboxes.append((classroom, var))

        self.first_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.last_name_entry.grid(row=1, column=1, padx=5, pady=5)

        # Set default values if provided
        self.first_name_entry.insert(0, self.first_name)
        self.last_name_entry.insert(0, self.last_name)

        return self.first_name_entry

    def apply(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()

        # Get the selected classrooms
        selected_classrooms = [classroom for classroom, var in self.classroom_checkboxes if var.get()]

        self.result = {'first_name': first_name, 'last_name': last_name, 'classrooms': selected_classrooms}

        if self.id:
            self.result['id'] = self.id

class ClassroomFormDialog(simpledialog.Dialog):
    def __init__(self, master, title, id=None, name="", default_name=None):
        self.id = id
        self.name = name
        self.default_name = default_name

        super().__init__(master, title)

    def body(self, master):
        tk.Label(master, text="Name:").grid(row=0, sticky="w")  # Change "First Name" to "Name"

        self.name_entry = tk.Entry(master, width=20)  # Change first_name_entry to name_entry

        self.name_entry.grid(row=0, column=1, padx=5, pady=5)  # Adjust row number

        self.name_entry.insert(0, self.name)

        return self.name_entry

    def apply(self):
        name = self.name_entry.get()

        self.result = {'name': name}

        if self.id:
            self.result['id'] = self.id

class HelpDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Help is here....baby").grid(row=0, sticky="w")

        return None

    def apply(self):
        return {}


class ItemDetailsDialog(simpledialog.Dialog):
    def __init__(self, master, title, item):
        self.item = item
        super().__init__(master, title)

    def body(self, master):
        # Display item details in the dialog
        tk.Label(master, text="Item Details", font=("Helvetica", 16, "bold")).pack()

        tk.Label(master, text=f"First Name: {self.item.first_name}").pack(pady=5)
        tk.Label(master, text=f"Last Name: {self.item.last_name}").pack(pady=5)
        tk.Label(master, text=f"Classroom: {self.item.classroom.name}").pack(pady=5)
