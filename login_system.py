# login_module.py
import logging
import customtkinter as ctk
from tkinter import messagebox
from database import Database
import sqlite3
import hashlib
import re

# Configure logging
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LoginSystem:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Login System")
        self.window.geometry("400x440")
        self.window.resizable(False, False)
        self.window.wm_iconbitmap("grocerify_logo.ico")
        
        # Configure appearance
        ctk.set_default_color_theme("green")
        
        # Initialize database
        self.db = Database()
        self.db.create_default_admin()
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.setup_login_gui()

    def setup_login_gui(self):
        # Logo or Title
        logo_label = ctk.CTkLabel(self.main_frame, 
                                 text="Welcome to Grocerify!",
                                 font=ctk.CTkFont(size=20, weight="bold"))
        logo_label.pack(pady=20)
        
        # Login Frame
        login_frame = ctk.CTkFrame(self.main_frame)
        login_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Username
        username_label = ctk.CTkLabel(login_frame, text="Username:",
                                    font=ctk.CTkFont(size=14))
        username_label.pack(pady=(20, 5))
        self.username_entry = ctk.CTkEntry(login_frame, width=200)
        self.username_entry.pack()
        
        # Password
        password_label = ctk.CTkLabel(login_frame, text="Password:",
                                    font=ctk.CTkFont(size=14))
        password_label.pack(pady=(20, 5))
        self.password_entry = ctk.CTkEntry(login_frame, width=200, show="•")
        self.password_entry.pack()
        
        # Login Button
        login_button = ctk.CTkButton(login_frame, text="Login",
                                   command=self.login,
                                   width=200)
        login_button.pack(pady=20)
        
        # Register Link
        register_button = ctk.CTkButton(login_frame, 
                                      text="Create New Account",
                                      command=self.show_register,
                                      width=200,
                                      fg_color="transparent",
                                      text_color=("gray10", "gray90"))
        register_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        user = self.db.check_user_credentials(username, password)
        
        if user:
            # Successful login
            self.db.update_last_login(username)
            logging.info(f"User '{username}' logged in successfully as '{user[1]}'")
            self.window.destroy()
            role = user[1]

            self.handle_user_role(username, role)
        else:
            logging.warning(f"Failed login attempt for username '{username}'")
            messagebox.showerror("Error", "Invalid username or password.")

    def handle_user_role(self, username, role):
        if role == "admin":
            # Start the inventory management system
            messagebox.showinfo(f"Welcome, admin.", f"Welcome to Grocerify, {username}.")
            from inventory import InventoryManager
            app = InventoryManager(username, role)  # Pass username and role
            app.run()

        elif role == "user":
            messagebox.showinfo(f"Welcome, user.", f"Welcome to Grocerify, {username}.")
            from inventory import InventoryManagerUser
            app = InventoryManagerUser(username, role)  # Pass username and role
            app.run()

    def show_register(self):
            # Destroy the login window
            self.window.destroy()

            # Create registration window
            self.reg_window = ctk.CTk()
            self.reg_window.title("Register New Account")
            self.reg_window.geometry("400x500")
            self.reg_window.resizable(False, False)
            self.reg_window.wm_iconbitmap("grocerify_logo.ico")
            
            # Registration frame
            reg_frame = ctk.CTkFrame(self.reg_window)
            reg_frame.pack(pady=20, padx=40, fill="both", expand=True)
            
            # Title
            title_label = ctk.CTkLabel(reg_frame, 
                                    text="Create New Account",
                                    font=ctk.CTkFont(size=20, weight="bold"))
            title_label.pack(pady=20)
            
            # Username
            username_label = ctk.CTkLabel(reg_frame, text="Username:")
            username_label.pack(pady=5)
            self.reg_username = ctk.CTkEntry(reg_frame, width=200)
            self.reg_username.pack()
            
            # Email
            email_label = ctk.CTkLabel(reg_frame, text="Email:")
            email_label.pack(pady=5)
            self.reg_email = ctk.CTkEntry(reg_frame, width=200)
            self.reg_email.pack()
            
            # Password
            password_label = ctk.CTkLabel(reg_frame, text="Password:")
            password_label.pack(pady=5)
            self.reg_password = ctk.CTkEntry(reg_frame, width=200, show="●")
            self.reg_password.pack()
            
            # Confirm Password
            conf_password_label = ctk.CTkLabel(reg_frame, text="Confirm Password:")
            conf_password_label.pack(pady=5)
            self.reg_conf_password = ctk.CTkEntry(reg_frame, width=200, show="●")
            self.reg_conf_password.pack()
            
            # Register Button
            register_button = ctk.CTkButton(reg_frame,
                                        text="Register",
                                        command=self.register_user,
                                        width=200)
            register_button.pack(pady=20)

            # Back Button
            back_button = ctk.CTkButton(reg_frame, text="Back", command=self.show_login, width=100, fg_color="red")
            back_button.pack(pady=6)

            # Start the main loop for the registration window
            self.reg_window.mainloop()

    def show_login(self):
        self.reg_window.destroy()
        self.__init__()
        self.run()

    def register_user(self, db_name="Grocerify_Database.db"):
        username = self.reg_username.get()
        email = self.reg_email.get()
        password = self.reg_password.get()
        conf_password = self.reg_conf_password.get()
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        
        # Validation
        if not all([username, email, password, conf_password]):
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        if password != conf_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        
        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            messagebox.showerror("Error", "Invalid email format.")
            return
        
        # Check if username exists
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Username already exists.")
            return
        
        # Check if email exists
        self.cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Email already registered.")
            return
        
        # Hash password and save user
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.cursor.execute("""
                INSERT INTO users (username, password, email, role)
                VALUES (?, ?, ?, ?)
            """, (username, hashed_password, email, 'user'))
            self.conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
            self.show_login()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create account: {str(e)}")
    

    def run(self):
        self.window.mainloop()