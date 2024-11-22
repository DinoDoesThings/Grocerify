# login_module.py
import customtkinter as ctk
from tkinter import messagebox
from database import Database

class LoginSystem:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Login System")
        self.window.geometry("400x440")
        self.window.resizable(False, False)
        
        # Configure appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
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
                                 text="Inventory Management System",
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
        
        # Forgot Password Link
        forgot_button = ctk.CTkButton(login_frame,
                                    text="Forgot Password?",
                                    command=self.forgot_password,
                                    width=200,
                                    fg_color="transparent",
                                    text_color=("gray10", "gray90"))
        forgot_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        user = self.db.check_user_credentials(username, password)
        
        if user:
            # Successful login
            self.db.update_last_login(username)
            self.window.destroy()

            # Start the inventory management system
            from inventory import InventoryManager
            app = InventoryManager(username, user[1])  # Pass username and role
            app.run()
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def show_register(self):
        # Registration GUI logic
        pass

    def forgot_password(self):
        # Forgot password GUI logic
        pass

    def run(self):
        self.window.mainloop()