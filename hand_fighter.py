from src.login_interface import LoginApp
import customtkinter as ctk

def run_login():
    root = ctk.CTk()
    login_interface = LoginApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_login()