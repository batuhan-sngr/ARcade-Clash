import tkinter as tk
from tkinter import ttk
from getpass import getpass
import sqlite3

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Page")

        self.label_username = ttk.Label(root, text="Username:")
        self.label_username.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.entry_username = ttk.Entry(root)
        self.entry_username.grid(row=0, column=1, padx=10, pady=10)

        self.label_password = ttk.Label(root, text="Password:")
        self.label_password.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.entry_password = ttk.Entry(root, show="*")
        self.entry_password.grid(row=1, column=1, padx=10, pady=10)

        self.button_login = ttk.Button(root, text="Login", command=self.login)
        self.button_login.grid(row=2, column=0, pady=10, padx=5, sticky="e")

        self.button_signup = ttk.Button(root, text="Signup", command=self.signup)
        self.button_signup.grid(row=2, column=1, pady=10, padx=5, sticky="w")

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        # Connect to the SQLite database
        conn = sqlite3.connect("user_database.db")
        cursor = conn.cursor()

        # Check if the username and password match
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        # Close the database connection
        conn.close()

        if user:
            print("Login successful!")
            self.root.destroy()  # Close the login window after successful login
            start_game()
        else:
            print("Invalid username or password. Please try again.")

    def signup(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        # Connect to the SQLite database
        conn = sqlite3.connect("user_database.db")
        cursor = conn.cursor()

        # Check if the username already exists
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            print("Username already exists. Please choose a different username.")
        else:
            # Insert new user into the database
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            print("Signup successful!")

        # Close the database connection
        conn.close()

def start_game():
    # You can add your game script here or call the function that starts the game
    print("Starting the game...")

def main():
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
