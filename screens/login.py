import tkinter as tk
from config.utils import hash_password
from config import constants
from db import get_connection
from db.models import User
from screens.dashboard import DashboardScreen

_ = lambda x: x

class LoginScreen:
    def __init__(self, root, session_manager):
        # Aplike fenèt rasin nan, nan nouvo ekran sa.
        self.root = root
        self.session_manager = session_manager

        self.root.title(f"{constants.APP_NAME} - {_('Login')}")

        width = 380
        height = 600

        # Rekipere lajè ekran
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Kalkil pou plase fenèt la nan mitan ekran computer a
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.root.geometry("%dx%d+%d+%d" % (width, height, x, y))

        # Kreye widjèt ki pou ekran sa
        self.create_widgets()

    def create_widgets(self):
        # Create a canvas for the login screen with a rectangle shape
        # self.canvas = tk.Canvas(self.root, width=400, height=600, bg="black")
        # self.canvas.grid(row=0, column=0, sticky='nsew')

        # # Add a logo image with a fixed size (replace 'logo.png' with your image file)
        # logo = tk.PhotoImage(file="assets/img/logo.png")
        # logo = logo.subsample(2, 2)  # Adjust the subsample values for the desired size
        # self.logo_label = tk.Label(self.root, image=logo, bg="white")
        # self.logo_label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Create email and password entry fields
        self.email_label = tk.Label(self.root, text="Email:")
        self.email_label.grid(row=1, column=0, sticky='w', padx=10, pady=10)

        self.email_entry = tk.Entry(self.root, width=40)
        self.email_entry.grid(row=2, column=0, padx=10, pady=10, columnspan=2)

        self.password_label = tk.Label(self.root, text="Password:")
        self.password_label.grid(row=3, column=0, sticky='w', padx=10, pady=10)

        self.password_entry = tk.Entry(self.root, show="*", width=40)
        self.password_entry.grid(row=4, column=0, padx=10, pady=10, columnspan=2)

        # Ajoute evènman ENTER sou chak input yo, pou deklanche submit login() nan
        self.email_entry.bind("<Return>", lambda event: self.login())
        self.password_entry.bind("<Return>",  lambda event: self.login())

        # Bouton CONNECT ki relye ak fonksyon login() nan
        self.connect_button = tk.Button(self.root, text="Connect", bg="blue", fg="white", command=self.login)
        self.connect_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def show_error_message(self, message):
        # Create a label to display the error message
        error_label = tk.Label(self.root, text=message, fg="red")
        error_label.grid(row=6, column=0, columnspan=2)

    def show_dashboard(self):
        # Close the current login window
        self.root.destroy()

        # Kreye epi deklanche nouvo ekran
        dashboard_window = tk.Tk()  # Create a new root window for the dashboard
        dashboard = DashboardScreen(dashboard_window, self.session_manager)  # Initialize the Dashboard

    def login(self):
        # Pran sa itilizatè a tape yo
        email = self.email_entry.get()
        password = self.password_entry.get()

        if email and password:
            # konveti an miniskil
            email = email.lower()

            # Hash the entered password
            hashed_password = hash_password(password)

            # Itilizasyon framework tbl pou rekipere user a, gras ak chan yo
            user = User.db.get(email=email, password=hashed_password)

            if user:
                # Successful login via tbl framework
                self.session_manager.login(user)

                # Redirect user a nan ekran dashboard li
                self.show_dashboard()
            else:
                # Failed login
                self.show_error_message(_("Invalid credentials. Please try again."))
                
        else:
            self.show_error_message(_("All the fields are required"))