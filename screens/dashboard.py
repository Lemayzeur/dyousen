from tkinter import ttk, messagebox, filedialog

from db import get_connection
from db.models import (
    Student, Teacher,
    Classroom,
)

from config import constants

from widgets.add_item_dialog import (
    StudentFormDialog,
    TeacherFormDialog,
    ClassroomFormDialog,
    ItemDetailsDialog,
    HelpDialog,
)

import tkinter as tk
import screens.login
import csv

_ = lambda x: x

class DashboardScreen:
    def __init__(self, root, session_manager):
        self.root = root
        self.root.title(f"{constants.APP_NAME} - {_('Dashboard')}")

        self.session_manager = session_manager

        if not self.session_manager.is_logged_in():
            messagebox.showwarning(_("Access Denied"), _("You are not authorized to this screen"), icon="warning")
            
            screens.login.LoginScreen(root, session_manager)

            return

        # Determine the screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Set the size and position of the dashboard window
        self.width = int(screen_width * 0.9)
        self.height = int(screen_height * 0.9)
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2

        self.root.geometry("%dx%d+%d+%d" % (self.width, self.height, x, y))

        self.create_top_menu()
        self.create_left_menu()
        self.create_main_content()

        # Data 
        self.selected_items = []
        self.selected_menu_item = None

    def create_top_menu(self):
        top_menu = tk.Menu(self.root)
        self.root.config(menu=top_menu)

        file_menu = tk.Menu(top_menu, tearoff=0)
        language_item = tk.Menu(top_menu, tearoff=0)
        help_item = tk.Menu(top_menu, tearoff=0)

        top_menu.add_cascade(label=_("Menu"), menu=file_menu)
        top_menu.add_cascade(label=_("Language"), menu=language_item)
        top_menu.add_cascade(label=_("Help"), menu=help_item)

        file_menu.add_command(label=_("Export as CSV"), command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label=_("Exit"), command=self.root.quit)

        language_item.add_command(label="English", command=self.open_file)
        language_item.add_command(label="Français", command=self.open_file)

        help_item.add_command(label=_("How to"), command=self.open_file)
        help_item.add_command(label=_("Donation"), command=self.open_file)

    def create_left_menu(self):
        # Create the left menu
        left_menu = tk.Frame(self.root, width=200, bg="white")
        left_menu.grid(row=0, column=0, rowspan=2, sticky="nsw")

        # Create a scrollable frame for the left menu
        menu_canvas = tk.Canvas(left_menu, bg="lightgray", width=200, height=self.height)
        menu_frame = tk.Frame(menu_canvas, bg="lightgray")
        menu_scrollbar = tk.Scrollbar(left_menu, orient="vertical", command=menu_canvas.yview)

        menu_canvas.create_window((0, 0), window=menu_frame, anchor="nw")
        menu_canvas.configure(yscrollcommand=menu_scrollbar.set)

        # plase menu an agoch, epi pou l okipe tout espas la nan vètikal
        menu_canvas.pack(side="left", fill="both", expand=True)
        menu_scrollbar.pack(side="right", fill="y")

        # Create menu items
        menu_items = ["Students", "Teachers", "Classrooms"]  # Replace with your menu items
        hovered_item = None

        # for i, item in enumerate(menu_items):
        #     menu_label = tk.Label(menu_frame, text=item, bg="lightgray")
        #     menu_label.grid(row=i, column=0, sticky="w")

        # self.left_menu = tk.Frame(self.root, width=200, bg="lightgray")
        # self.left_menu.grid(row=0, column=0, rowspan=2, sticky="nsw")

        for i, item in enumerate(menu_items):
            menu_label = tk.Button(menu_frame, text=item.title(), bg="white",
                 command=lambda current_item=item.title(): self.on_menu_click(current_item), width=22)
            menu_label.grid(row=i, column=0, sticky="w")

        # Configure the column to expand horizontally

    def create_main_content(self):
        self.main_content = tk.Frame(self.root, bg="white", width=100)
        self.main_content.grid(row=0, column=1, rowspan=2, sticky="nsew")

        # Create a frame for the buttons (Add, Delete, Update)
        buttons_frame = tk.Frame(self.main_content)
        buttons_frame.grid(row=0, column=0, padx=(0, 5), pady=5)

        # Create buttons and entry for Add, Delete, and Search
        self.add_button = tk.Button(buttons_frame, text="Add", command=self.add_item, width=10, state=tk.DISABLED)
        self.add_button.grid(row=0, column=0, padx=(0, 2), pady=5)

        self.update_button = tk.Button(buttons_frame, text="Update", command=self.update_item, width=10, state=tk.DISABLED)
        self.update_button.grid(row=0, column=1, padx=(2, 5), pady=5)

        self.delete_button = tk.Button(buttons_frame, text="Delete", command=self.delete_item, width=10, state=tk.DISABLED)
        self.delete_button.grid(row=0, column=2, padx=2, pady=5)

        # Create a frame for the entry and search button
        entry_frame = tk.Frame(self.main_content)
        entry_frame.grid(row=0, column=1, padx=(0, 5), pady=5)

        self.search_entry = tk.Entry(entry_frame)
        self.search_entry.grid(row=0, column=3, padx=5, pady=5)

        self.search_button = tk.Button(entry_frame, text="Search", command=lambda: self.search_item(self.search_entry.get()), width=10, state=tk.DISABLED)
        self.search_button.grid(row=0, column=4, padx=5, pady=5)

        # Create a Treeview widget with columns
        self.treeview = ttk.Treeview(self.main_content, show="headings")
        self.treeview.grid(row=1, column=0, columnspan=4, pady=5)

        # Create vertical scrollbar
        scrollbar = tk.Scrollbar(self.main_content, command=self.treeview.yview)
        scrollbar.grid(row=1, column=4, sticky="ns")

        # Configure the Treeview to use the vertical scrollbar
        self.treeview.configure(yscrollcommand=scrollbar.set)

        # Bind the resize function to the window resizing event
        self.main_content.columnconfigure(0, weight=1)
        self.main_content.columnconfigure(1, weight=1)
        self.main_content.columnconfigure(2, weight=1)
        self.main_content.columnconfigure(3, weight=1)
        self.main_content.columnconfigure(4, weight=1)

        # Bind the key events to the entry widget
        self.search_entry.bind("<Return>", lambda event: self.search_item(self.search_entry.get()))
        self.search_entry.bind("<Control-a>", self.select_all)

        self.treeview.bind("<<TreeviewSelect>>", self.on_select_item)
        self.treeview.bind("<Double-1>", self.on_double_click_item)

        self.caption_label = tk.Label(self.main_content, text="Total: 0")
        self.caption_label.grid(row=2, column=0, padx=5, pady=5)

        # # Add some sample items to the Listbox
        # for item in ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]:
        #     self.listbox.insert(tk.END, item)

        # Make the Listbox expand horizontally
        self.main_content.columnconfigure(0, weight=1)

    def update_treeview(self, columns, items):
        # Clear existing data in the Treeview
        self.treeview.delete(*self.treeview.get_children())

        # Configure the Treeview columns based on the dynamic column names
        self.treeview["columns"] = tuple(range(1, len(columns) + 2))
        self.treeview.column(1, stretch=True)

        self.treeview.heading(1, text="#")  # Index column
        
        for col, col_name in enumerate(columns, 1):
            col_name = col_name.split('.')[0]
            self.treeview.heading(col + 1, text=col_name.replace('_', ' ').replace('[', '').replace(']', '').title())
            self.treeview.column(col + 1, stretch=True)  # Set the initial column width

        # print('self,items', self.items)
        for i, item in enumerate(items):
            index = i + 1
            item_values = [index]  # Start with the index value
            for col_name in columns:
                if '[' in col_name and '.' in col_name:
                    col_name = col_name[1:-1]
                    field, nested_col_name = col_name.split('.')
                    instances = getattr(item, field)
                    value = ", ".join([getattr(instance, nested_col_name, "") for instance in instances])
                elif '.' in col_name: # classroom.name
                    field, nested_col_name = col_name.split('.')
                    instance = getattr(item, field)

                    value = getattr(instance, nested_col_name, "") if instance else ""
                else:
                    value = getattr(item, col_name, "")

                item_values.append(value)

            # print('item', item.id, item.first_name, item.last_name, item.classroom.name)
            self.treeview.insert("", index=index, iid=item.id, values=item_values)

    def on_select_item(self, a):
        self.selected_items = self.treeview.selection()

        state = tk.NORMAL if self.selected_items else tk.DISABLED
        self.update_button['state'] = state 
        self.delete_button['state'] = state 

    def on_double_click_item(self, event):
        # rekipere eleman ki klike a
        selected_item = self.treeview.item(self.treeview.selection())

        # rekipere bon valè nou bezwen an, anndan kle "values"
        index = selected_item["values"][0] 

        # find the item based on the index
        item = next((item_value for item_index, item_value in enumerate(self.items) if item_index == index), None)

        # Open a new modal to view item details
        if item is not None:
            dialog = ItemDetailsDialog(self.root, "Item Details", item)
            dialog.mainloop()
        else:
            print("Item not found for index:", index)

    def clear_treeview(self):
        self.treeview.delete(*self.treeview.get_children())

    def open_file(self):
        HelpDialog(self.root)
        pass

    def add_item(self):
        if not self.selected_menu_item:
            messagebox.showinfo(_("No Selection"), _("Please choose an item in the left menu first"), icon="info")
            return

        classrooms = Classroom.db.all(order_by='name')

        if self.selected_menu_item == 'Students':

            dialog = StudentFormDialog(self.root, _('Add Student'), classrooms=classrooms)
        elif self.selected_menu_item == 'Teachers':
            dialog = TeacherFormDialog(self.root, _('Add Teacher'), classrooms=classrooms)
        else:
            dialog = ClassroomFormDialog(self.root, _('Add Classroom'))
        
        result = dialog.result
        
        if result:
            # Create the model instance based on the selected menu item
            if self.selected_menu_item == 'Students':
                item_model = Student
                item_instance = item_model.db.create(**result)
            elif self.selected_menu_item == 'Teachers':
                item_model = Teacher
                classrooms = result['classrooms']

                item_instance = item_model.db.create(**result)

                item_instance.m2m_clear('classrooms')
                item_instance.m2m_add('classrooms', *classrooms)
            else:
                item_model = Classroom
                item_instance = item_model.db.create(**result)

            

            self.items.append(item_instance)

            index = len(self.items)

            if self.selected_menu_item == 'Students':
                item_values = [index, item_instance.first_name, item_instance.last_name, item_instance.classroom.name]
            elif self.selected_menu_item == 'Teachers':
                item_values = [index, item_instance.first_name, item_instance.last_name, 
                                    ", ".join([getattr(instance, 'name', "") for instance in item_instance.classrooms])]
            else:
                item_values = [index, item_instance.name]

            # Insert the new item into the Treeview
            self.treeview.insert("", index=index, iid=item_instance.id, values=item_values)

            # Scroll to the very bottom of the Treeview
            self.treeview.yview_moveto(1)

    def update_item(self):
        if not self.selected_items:
            messagebox.showinfo(_("No Selection"), _("Please select the item you want to delete"), icon="info")
            return 

        if len(self.selected_items) > 1:
            messagebox.showinfo(_("Too many selections"), _("Please select one item to update"), icon="info")
            return 

        index, selected_item = self.get_index_by_id(int(self.selected_items[0]))

        # Check the selected menu item and create the appropriate dialog
        if self.selected_menu_item == 'Students':
            classrooms = Classroom.db.all(order_by='name')
            dialog = StudentFormDialog(
                self.root, "Update Student",
                id=selected_item.id,
                first_name=selected_item.first_name,
                last_name=selected_item.last_name,
                classroom_id=selected_item.classroom.id,
                classrooms=classrooms
            )
        elif self.selected_menu_item == 'Teachers':
            classrooms = Classroom.db.all(order_by='name')
            dialog = TeacherFormDialog(
                self.root, "Update Teacher",
                id=selected_item.id,
                first_name=selected_item.first_name,
                last_name=selected_item.last_name,
                classrooms=classrooms,
                assigned_classrooms=[el.id for el in selected_item.classrooms],
            )
        else:
            dialog = ClassroomFormDialog(
                self.root, "Update Classroom",
                id=selected_item.id,
                name=selected_item.name
            )

        result = dialog.result

        if result:
            # If updating a student, handle the classroom separately
            if self.selected_menu_item == 'Students':
                classroom = result.pop('classroom')
                result['classroom_id'] = classroom.id

            print('result', result)
            # Update the item in the database
            item_model = Student if self.selected_menu_item == 'Students' else Teacher if self.selected_menu_item == 'Teachers' else Classroom
            item_instance = item_model.db.update({'id': selected_item.id}, {**result})

            # Get the updated values for the Treeview based on the selected menu item
            #  item_values = [index] + [getattr(item_instance, col) for col in self.columns]

            if self.selected_menu_item == 'Students':
                item_values = [index + 1, result['first_name'], result['last_name'], classroom.name]
            elif self.selected_menu_item == 'Teachers':
                print('result', result)
                item_values = [index + 1, result['first_name'], result['last_name'],
                                ", ".join([getattr(instance, 'name', "") for instance in result['classrooms']])]
            else:
                item_values = [index + 1, result['name']]

            self.update_item_values(result['id'], item_values)

    def find_item_by_iid(self, target_iid):
        # Use the item method to retrieve information about the item
        try:
            found_item = self.treeview.item(target_iid)
            return found_item
        except tk.TclError:
            # Handle the case where the iid is not found
            return None

    def get_index_by_id(self, item_id):
        for index, item in enumerate(self.items):
            if item.id == item_id:
                return index, item
        return None  # Return None if the item with the specified id is not found in self.items


    def set_treeview_items(self, new_items):
        # Adjust this based on your data
        self.items = new_items

        # Chanje teks total pou COUNTER yo
        self.caption_label.config(text=f"{_('Total')}: {len(self.items)}")

    def delete_item(self):
        if not self.selected_items:
            messagebox.showinfo(_("No Selection"), _("Please select the item you want to delete"), icon="info")
            return

        # Placeholder function for confirming deletion
        result = messagebox.askquestion(_("Confirm Delete"), _("Are you sure you want to delete this item?"), icon="warning")

        if result == "yes":
            match self.selected_menu_item:
                case 'Students':
                    # Student.db.bulk_delete(self.selected_items)

                    [self.remove_item_by_iid(iid) for iid in self.selected_items]

                    self.set_treeview_items(list(filter(lambda item: item.id not in self.selected_items, self.items)))

                    return "Option 1 selected"
                case 'Teachers':
                    Teacher.db.bulk_delete(self.selected_items)

                    # Clear the list
                    self.clear_treeview()

                    self.fetch_teachers()
                    return "Option 2 selected"
                case 'Classrooms':
                    Classroom.db.bulk_delete(self.selected_items)

                    # Clear the list
                    self.clear_treeview()

                    self.fetch_classrooms()
                    return "Option 3 selected"
                case _:
                    print('Invalid option')
                    return "Invalid option"
        else:
            print("Deletion canceled")

    def search_item(self, query):
        if query:
            query = query.strip()
            match self.selected_menu_item:
                case 'Students':
                    # Clear the list
                    self.clear_treeview()

                    self.set_treeview_items(Student.db.search(keyword=query, search_cols=['first_name', 'last_name', 'classroom.name']))

                    self.update_treeview(['first_name', 'last_name', 'classroom.name'], self.items)

                    return "Option 1 selected"
                case 'Teachers':
                    # Clear the list
                    self.clear_treeview()

                    self.set_treeview_items(Student.db.search(keyword=query, search_cols=['first_name', 'last_name']))

                    self.update_treeview(['first_name', 'last_name', 'classroom.name'], self.items)
                    return "Option 2 selected"
                case 'Classrooms':
                    # Clear the list
                    self.clear_treeview()

                    self.set_treeview_items(Student.db.search(keyword=query, search_cols=['name']))

                    self.update_treeview(['name'], self.items)
                    return "Option 3 selected"
                case _:
                    print('Invalid option')
                    return "Invalid option"

    def update_item_values(self, target_iid, updated_values):
        # Use the item method to update the values of the item
        try:
            self.treeview.item(target_iid, values=updated_values)
        except tk.TclError:
            # Handle the case where the iid is not found
            print(f"Item with iid '{target_iid}' not found.")

    def remove_item_by_iid(self, target_iid):
        # Use the delete method to remove the item
        try:
            self.treeview.delete(target_iid)
        except tk.TclError:
            pass 

    def fetch_students(self):
        # tbl framework
        items = Student.db.all()

        self.set_treeview_items(items)

        self.update_treeview(['first_name', 'last_name', 'classroom.name'], self.items)

    def fetch_teachers(self):
        # Close the current login window
        # self.root.destroy()
        self.set_treeview_items(Teacher.db.all())

        self.update_treeview(['first_name', 'last_name', '[classrooms.name]'], self.items)

    def fetch_classrooms(self):
        # Close the current login window
        # self.root.destroy()

        self.set_treeview_items(Classroom.db.all(order_by='name'))

        self.update_treeview(['name'], self.items)

    def on_menu_click(self, action):
        self.selected_menu_item = action

        self.add_button['state'] = tk.NORMAL 
        self.search_button['state'] = tk.NORMAL 
        
        match self.selected_menu_item:
            case 'Students':
                self.fetch_students()
                return
            case 'Teachers':
                self.fetch_teachers()
                return "Option 2 selected"
            case 'Classrooms':
                self.fetch_classrooms()
                return "Option 3 selected"
            case _:
                print('Invalid option')
                return "Invalid option"

    def select_all(self, event):
        self.search_entry.focus_set()
        self.search_entry.select_range(0, 'end')

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            data = [{'First Name': item.first_name, 'Last Name': item.last_name, 'Classroom': item.classroom.name} for item in self.items]
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)