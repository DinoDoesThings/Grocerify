import customtkinter as ctk
from customtkinter import *
import sqlite3
import csv
from datetime import datetime
import random
from tkinter import messagebox
from tkinter import ttk  # Added missing import

# Configure CustomTkinter appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

class InventoryManager:
    def __init__(self):
        # Initialize main window
        self.window = ctk.CTk()
        self.window.title("Grocerify - Modern Inventory Manager")
        self.window.geometry("1000x800")
        
        # Database setup
        self.conn = sqlite3.connect("inventory.db")
        self.cursor = self.conn.cursor()
        self.setup_database()
        
        # Variables for entry fields
        self.placeholderArray = [ctk.StringVar() for _ in range(5)]
        
        self.setup_gui()
        
    def setup_database(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            category TEXT NOT NULL,
            date_added TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def setup_gui(self):
        # Main container
        self.main_container = ctk.CTkFrame(self.window)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(self.main_container, 
                            text="Grocerify",
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=10)
        
        # Create frames
        self.create_entry_frame()
        self.create_button_frame()
        self.create_table_frame()
        
    def create_entry_frame(self):
        entry_frame = ctk.CTkFrame(self.main_container)
        entry_frame.pack(fill="x", padx=20, pady=10)
        
        labels = ["Item ID", "Name", "Price", "Quantity", "Category"]
        self.entries = []
        
        # Create grid layout for labels and entries
        for i, label in enumerate(labels):
            ctk.CTkLabel(entry_frame, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            
            if label == "Category":
                entry = ctk.CTkOptionMenu(entry_frame,
                                        values=["Meat", "Vegetables", "Fruits", "Dairy Products","Beverages"], 
                                        variable=self.placeholderArray[i],
                                        width=300)
            else:
                entry = ctk.CTkEntry(entry_frame, textvariable=self.placeholderArray[i], width=300)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            self.entries.append(entry)
            
            if i == 0:  # Add Generate ID button next to Item ID
                generate_btn = ctk.CTkButton(entry_frame, 
                                           text="Generate ID",
                                           command=self.generateId,
                                           width=100)
                generate_btn.grid(row=i, column=2, padx=10, pady=5)

    def create_button_frame(self):
        button_frame = ctk.CTkFrame(self.main_container)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        # Create buttons with consistent styling
        buttons = [
            ("Save", self.saveData),
            ("Update", self.updateData),
            ("Delete", self.deleteData),
            ("Select", self.selectData),
            ("Clear", self.clearFields),
            ("Export", self.exportToExcel)
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(button_frame,
                               text=text,
                               command=command,
                               width=120,
                               height=32)
            btn.pack(side="left", padx=5, pady=5)

    def create_table_frame(self):
        # Create a frame specifically for the table
        table_frame = ctk.CTkFrame(self.main_container)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create a nested tk.Frame for the Treeview
        tree_frame = ttk.Frame(table_frame)
        tree_frame.pack(fill="both", expand=True)
        
        # Create Treeview with modern styling
        self.tree = ttk.Treeview(tree_frame, show='headings', height=20)
        self.tree["columns"] = ["Item Id", "Name", "Price", "Quantity", "Category", "Date"]

        # Configure the Treeview style
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        # Configure columns
        for col in self.tree["columns"]:
            self.tree.column(col, anchor="w", width=120)
            self.tree.heading(col, text=col, anchor="w")
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        
        # Configure the treeview to use scrollbars
        self.tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Grid layout for treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.refreshTable()

    def refreshTable(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.cursor.execute("SELECT * FROM inventory")
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def saveData(self):
        item_id = self.placeholderArray[0].get()
        name = self.placeholderArray[1].get()
        price = self.placeholderArray[2].get()
        quantity = self.placeholderArray[3].get()
        category = self.placeholderArray[4].get()
        date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not all([item_id, name, price, quantity, category]):
            messagebox.showerror("Error", "Please fill all fields.")
            return

        try:
            self.cursor.execute("""
                INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?)
            """, (item_id, name, float(price), int(quantity), category, date_added))
            self.conn.commit()
            self.refreshTable()
            self.clearFields()
            messagebox.showinfo("Success", "Item saved successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Item ID already exists!")
        except ValueError:
            messagebox.showerror("Error", "Invalid price or quantity format!")

    def updateData(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item to update!")
            return

        item_id = self.tree.item(selected_item[0])['values'][0]
        name = self.placeholderArray[1].get()
        price = self.placeholderArray[2].get()
        quantity = self.placeholderArray[3].get()
        category = self.placeholderArray[4].get()

        try:
            self.cursor.execute("""
                UPDATE inventory 
                SET name=?, price=?, quantity=?, category=?
                WHERE item_id=?
            """, (name, float(price), int(quantity), category, item_id))
            self.conn.commit()
            self.refreshTable()
            self.clearFields()
            messagebox.showinfo("Success", "Item updated successfully!")
        except ValueError:
            messagebox.showerror("Error", "Invalid price or quantity format!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update item: {str(e)}")

    def deleteData(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item to delete!")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            item_id = self.tree.item(selected_item[0])['values'][0]
            self.cursor.execute("DELETE FROM inventory WHERE item_id=?", (item_id,))
            self.conn.commit()
            self.refreshTable()
            self.clearFields()
            messagebox.showinfo("Success", "Item deleted successfully!")

    def selectData(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item!")
            return

        values = self.tree.item(selected_item[0])['values']
        for i, value in enumerate(values[:5]):
            self.placeholderArray[i].set(value)

    def clearFields(self):
        for var in self.placeholderArray:
            var.set("")

    def generateId(self):
        self.placeholderArray[0].set(f"ITEM-{random.randint(1000, 9999)}")

    def exportToExcel(self):
        try:
            # Get current timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"inventory_export_{timestamp}.csv"
            
            # Open file dialog for saving
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile=default_filename,
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Inventory Data"
            )
            
            if not file_path:  # If user cancels the dialog
                return
            
            # Fetch all data from database with date_added
            self.cursor.execute("""
                SELECT 
                    item_id,
                    name,
                    price,
                    quantity,
                    category,
                    date_added
                FROM inventory
                ORDER BY date_added DESC
            """)
            rows = self.cursor.fetchall()
            
            # Write to CSV with proper formatting
            with open(file_path, "w", newline="", encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Write headers
                writer.writerow([
                    "Item ID",
                    "Name",
                    "Price",
                    "Quantity",
                    "Category",
                    "Date Added"
                ])
                
                # Write data rows with formatted values
                for row in rows:
                    item_id, name, price, quantity, category, date_added = row
                    
                    # Format price to 2 decimal places
                    formatted_price = f"{float(price):.2f}"
                    
                    # Convert date string to datetime and format it
                    try:
                        date_obj = datetime.strptime(date_added, "%Y-%m-%d %H:%M:%S")
                        formatted_date = date_obj.strftime("%Y-%m-%d %I:%M:%S %p")
                    except ValueError:
                        formatted_date = date_added  # Keep original if parsing fails
                    
                    writer.writerow([
                        item_id,
                        name,
                        formatted_price,
                        quantity,
                        category,
                        formatted_date
                    ])
            
            # Get file size for the success message
            file_size = os.path.getsize(file_path) / 1024  # Convert to KB
            
            messagebox.showinfo(
                "Export Successful",
                f"Data exported successfully!\n\n"
                f"Location: {file_path}\n"
                f"Items exported: {len(rows)}\n"
                f"File size: {file_size:.1f} KB\n\n"
            )
            
            # Ask if user wants to open the exported file
            if messagebox.askyesno("Open File", "Would you like to open the exported file?"):
                os.startfile(file_path)
                
        except PermissionError:
            messagebox.showerror(
                "Export Error",
                "Could not save the file. Please check if the file is open in another program."
            )
        except Exception as e:
            messagebox.showerror(
                "Export Error",
                f"An error occurred while exporting: {str(e)}"
            )

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = InventoryManager()
    app.run()