import customtkinter as ctk
import tkinter as tk
from getpass import getpass
import sqlite3
from fighter_game import FighterGame

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1410x940")
        self.center_window()
        self.root.configure(bg="#99CCFF") # Set appearance mode to dark

        self.create_widgets()

        # Initialize StringVar for storing the remembered username
        self.remembered_username = tk.StringVar()
        self.load_remembered_username()

        # Initialize StringVar for storing the selected camera index
        self.selected_camera = tk.StringVar()
        self.selected_camera.set("Default")  # Default value, change it as needed

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_center = (screen_width - 1410) // 2
        y_center = (screen_height - 940) // 2
        self.root.geometry(f"1410x940+{x_center}+{y_center}")
    
    def create_users_table(self):
        # Connect to the SQLite database
        conn = sqlite3.connect("user_database.db")
        cursor = conn.cursor()

        # Create the "users" table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)

        # Commit changes and close the database connection
        conn.commit()
        conn.close()

    def load_remembered_username(self):
        # Load the remembered username from a file or any other persistent storage
        # For simplicity, let's use a file named "remembered_username.txt"
        try:
            with open("remembered_username.txt", "r") as file:
                remembered_username = file.read().strip()
                if remembered_username:
                    self.remembered_username.set(remembered_username)
        except FileNotFoundError:
            pass

    def save_remembered_username(self, username):
        # Save the remembered username to a file or any other persistent storage
        # For simplicity, let's use a file named "remembered_username.txt"
        with open("remembered_username.txt", "w") as file:
            file.write(username)

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
        self.create_users_table()  # Make sure the "users" table exists

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

            # Update the signup button to act as a login button
            self.signup_button.config(text="Login", command=self.login)

        # Close the database connection
        conn.close()

    def enter_anonymous(self):
        self.root.destroy()  # Close the current LoginApp window
        root = tk.Tk()
        start_game()
        print("test_anonymous")
        root.mainloop()

    def create_widgets(self):
        frame = ctk.CTkFrame(master=self.root, width=800, height=650)
        frame.pack_propagate(False)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        label = ctk.CTkLabel(master=frame, text="WELCOME TO ARCADE CLASH",
                                        font=("Fixedsys", 40))
        label.pack(pady=25)

        # Define entry_username and entry_password as instance variables
        self.entry_username = ctk.CTkEntry(master=frame, placeholder_text="Username", font=("Fixedsys", 25))
        self.entry_username.pack(pady=12, padx=10)

        self.entry_password = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*", font=("Fixedsys", 25))
        self.entry_password.pack(pady=12, padx=10)

        button = ctk.CTkButton(master=frame, text="Login", command=self.login, font=("Fixedsys", 30, "bold"),
                                        fg_color="#E88655", hover_color="#EBA17C")
        button.pack(pady=12, padx=10)

        anonymous = ctk.CTkButton(master=frame, text="Anonymous", command=self.enter_anonymous,
                                            font=("Fixedsys", 30, "bold"), fg_color="#2190C7", hover_color="#5BB2DE")
        anonymous.pack(pady=12, padx=10)

        checkbox = ctk.CTkCheckBox(master=frame, text="Remember Me", font=("Fixedsys", 30), fg_color="#E88655",
                                            hover_color="#EBA17C")
        checkbox.pack(pady=12, padx=10)

        # Add a label above the "Sign In" button
        label_dont_have_account = ctk.CTkLabel(master=frame, text="Don't have an account yet?",
                                                        font=("Fixedsys", 20))
        label_dont_have_account.pack(pady=10)

        # Add a "Sign In" button below the label
        sign_in_button = ctk.CTkButton(master=frame, text="Sign Up", command=self.signup,
                                                 font=("Fixedsys", 30, "bold"), fg_color="#E88655", hover_color="#EBA17C")
        sign_in_button.pack(pady=5)  # Specify a smaller pady value to keep the button visible

def start_game():
    game = FighterGame()
    game.run_game()

def main():
    root = ctk.CTk()
    app = LoginApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
