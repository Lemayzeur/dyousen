from screens.login import LoginScreen
from screens.dashboard import DashboardScreen
from db.manager import SessionManager
from migrations.migrate import run_migrate
import tkinter as tk

if __name__ == "__main__":
    # Migrasyon bas done a, pou si gen nouvo tab ki dwe kreye
    run_migrate()

    # Inisyalize fenèt rasin aplikasyon an
    root = tk.Tk()

    # Enstans ki la pou tcheke si user a otantifye deja
    session_manager = SessionManager()

    # Tcheke si user a loge
    if session_manager.is_logged_in():
        # Si wi, voye l nan dashboard li
        dashboard_screen = DashboardScreen(root, session_manager)
    else:
        # Sinon, voye l nan ekran login, pou l konekte
        login_screen = LoginScreen(root, session_manager)

    # Loop aplikasyon an
    root.mainloop()
