import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import cv2
from PIL import Image, ImageTk
import time
import os
from datetime import datetime
from cube_processor import CubeProcessor

class CubifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cubifier")
        self.root.geometry("800x800")
        
        # Initialize instance variables
        self.timer_window = None
        self.cap = None
        self.timer_running = False
        self.start_time = 0
        self.time_var = tk.StringVar(value="0:00.00")
        self.logo_path = "Screenshot 2025-02-08 002811.png"  # Store path as class variable
        self.cube_processor = None
        self.video_label = None
        
        # Initialize database and UI
        self.create_database()
        self.root.after(1, self.set_app_icon)
        self.show_login_page()
        


    def set_app_icon(self):
        try:
            image = Image.open(self.logo_path)
            self.logo_image = ImageTk.PhotoImage(image)
            self.root.iconphoto(True, self.logo_image)
        except FileNotFoundError:
            print(f"Logo not found at path: {self.logo_path}")

    def load_and_resize_image(self, width=100, height=100):
        try:
            image = Image.open(self.logo_path)
            return ImageTk.PhotoImage(image.resize((width, height), Image.LANCZOS))
        except FileNotFoundError:
            print(f"Image not found at path: {self.logo_path}")
            return None

    def create_database(self):
        with sqlite3.connect('cubifier.db') as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS users
                        (username TEXT PRIMARY KEY, password TEXT)''')
            conn.commit()

    def show_login_page(self):
        self.clear_window()
        
        login_frame = ttk.Frame(self.root, padding="20")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Load logo image
        logo_image = self.load_and_resize_image()
        if logo_image:
            image_label = ttk.Label(login_frame, image=logo_image)
            image_label.image = logo_image
            image_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Label(login_frame, text="Login", font=('Helvetica', 16, 'bold')).grid(row=1, column=0, columnspan=2, pady=10)
        
        # Username field
        ttk.Label(login_frame, text="Username:").grid(row=2, column=0, pady=5)
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.grid(row=2, column=1, pady=5)
        
        # Password field
        ttk.Label(login_frame, text="Password:").grid(row=3, column=0, pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.grid(row=3, column=1, pady=5)
        
        # Buttons
        ttk.Button(login_frame, text="Login", command=self.login).grid(row=4, column=0, pady=10)
        ttk.Button(login_frame, text="Sign Up", command=self.show_signup_page).grid(row=4, column=1, pady=10)

    def show_signup_page(self):
        self.clear_window()
        
        signup_frame = ttk.Frame(self.root, padding="20")
        signup_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Load logo image
        logo_image = self.load_and_resize_image()
        if logo_image:
            image_label = ttk.Label(signup_frame, image=logo_image)
            image_label.image = logo_image
            image_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Label(signup_frame, text="Sign Up", font=('Helvetica', 16, 'bold')).grid(row=1, column=0, columnspan=2, pady=10)
        
        # Username field
        ttk.Label(signup_frame, text="Username:").grid(row=2, column=0, pady=5)
        self.new_username_entry = ttk.Entry(signup_frame)
        self.new_username_entry.grid(row=2, column=1, pady=5)
        
        # Password field
        ttk.Label(signup_frame, text="Password:").grid(row=3, column=0, pady=5)
        self.new_password_entry = ttk.Entry(signup_frame, show="*")
        self.new_password_entry.grid(row=3, column=1, pady=5)
        
        # Buttons
        ttk.Button(signup_frame, text="Sign Up", command=self.signup).grid(row=4, column=0, pady=10)
        ttk.Button(signup_frame, text="Back to Login", command=self.show_login_page).grid(row=4, column=1, pady=10)

    def show_home_page(self):
        self.clear_window()
        
        # Create top navigation bar
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(fill='x', pady=10)
        
        ttk.Button(nav_frame, text="Virtual Reality", command=self.show_vr_cube).pack(side='left', padx=10)
        ttk.Button(nav_frame, text="Cube Solver Assistant", command=self.show_cube_solver).pack(side='left', padx=10)
        ttk.Button(nav_frame, text="Timer", command=self.show_timer).pack(side='left', padx=10)
        ttk.Button(nav_frame, text="Logout", command=self.logout).pack(side='right', padx=10)
        #Music button
        self.music_button = ttk.Button(nav_frame, text="Play Music", command=self.toggle_music)
        self.music_button.pack(side='right', padx=10)
        # Welcome message and main content area
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Welcome to Cubifier!", 
                 font=('Helvetica', 16, 'bold')).pack(pady=20)
        
        ttk.Label(main_frame, text="Select an option from the menu above to begin", 
                 font=('Helvetica', 12)).pack(pady=10)
    def logout(self):
        # ... (Existing logout code)
        pass

    def __del__(self):
        # Cleanup when the application is closed
        if self.cap is not None:
            self.cap.release()
        

    def show_vr_cube(self):
        messagebox.showinfo("Coming Soon", "This feature is coming soon!")

    def show_cube_solver(self):
        self.clear_window()
        
        # Create main frame
        solver_frame = ttk.Frame(self.root, padding="20")
        solver_frame.pack(fill='both', expand=True)
        
        # Add back button
        back_button = ttk.Button(solver_frame, text="Back to Home", 
                               command=self.show_home_page)
        back_button.pack(anchor='nw', pady=(0, 10))
        
        # Initialize video capture
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
        
        # Initialize cube processor if needed
        if self.cube_processor is None:
            self.cube_processor = CubeProcessor()
        
        # Create video frame
        self.video_label = ttk.Label(solver_frame)
        self.video_label.pack(pady=10)
        
        # Create control buttons
        control_frame = ttk.Frame(solver_frame)
        control_frame.pack(pady=10)
        
        # Calibration buttons
        calibration_frame = ttk.LabelFrame(control_frame, text="Color Calibration")
        calibration_frame.pack(pady=10, padx=10)
        
        colors = ['white', 'yellow', 'red', 'orange', 'blue', 'green']
        for i, color in enumerate(colors):
            ttk.Button(calibration_frame, 
                      text=f"Calibrate {color.capitalize()}", 
                      command=lambda c=color: self.calibrate_color(c)).grid(row=i//3, 
                                                                          column=i%3, 
                                                                          padx=5, 
                                                                          pady=5)
        
        # Training and control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Train Model", 
                  command=self.train_color_model).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Reset Camera", 
                  command=self.reset_camera).pack(side='left', padx=5)
        
        # Start video update
        self.update_video()

    def show_timer(self):
        if self.timer_window is None or not self.timer_window.winfo_exists():
            self.timer_window = tk.Toplevel(self.root)
            self.timer_window.title("Cubifier Timer")
            self.timer_window.geometry("300x150")
            
            time_label = ttk.Label(self.timer_window, textvariable=self.time_var, 
                                 font=('Helvetica', 24))
            time_label.pack(pady=20)
            
            instruction_label = ttk.Label(self.timer_window, 
                                        text="Press SPACE to start/stop", 
                                        font=('Helvetica', 12))
            instruction_label.pack()
            
            self.timer_window.bind('<space>', self.toggle_timer)
            self.timer_window.focus_set()

    def update_video(self):
        if self.cap is not None and self.video_label is not None:
            ret, frame = self.cap.read()
            if ret:
                # Process frame
                processed_frame = self.cube_processor.process_frame(frame)
                
                # Convert to PhotoImage
                image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                # Resize image to fit the window better
                image = image.resize((640, 480), Image.LANCZOS)
                image = ImageTk.PhotoImage(image)
                
                # Update label
                self.video_label.configure(image=image)
                self.video_label.image = image
        
        # Schedule next update if video label still exists
        if self.video_label is not None and self.video_label.winfo_exists():
            self.root.after(10, self.update_video)

    def calibrate_color(self, color_name):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                self.cube_processor.calibrate_color(frame, color_name)
                messagebox.showinfo("Calibration", 
                                  f"{color_name.capitalize()} color calibrated successfully!")

    def train_color_model(self):
        if self.cube_processor.color_trainer.train_model():
            messagebox.showinfo("Training", "Color model trained successfully!")
        else:
            messagebox.showerror("Error", "No training data available!")

    def reset_camera(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.cap = cv2.VideoCapture(0)

    def toggle_timer(self, event):
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()
        else:
            self.timer_running = False

    def update_timer(self):
        if self.timer_running and hasattr(self, 'timer_window') and self.timer_window.winfo_exists():
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            hundredths = int((elapsed * 100) % 100)
            self.time_var.set(f"{minutes}:{seconds:02d}.{hundredths:02d}")
            self.root.after(10, self.update_timer)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        with sqlite3.connect('cubifier.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", 
                     (username, password))
            if c.fetchone():
                self.show_home_page()
            else:
                messagebox.showerror("Error", "Invalid username or password")

    def signup(self):
        username = self.new_username_entry.get()
        password = self.new_password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        with sqlite3.connect('cubifier.db') as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users VALUES (?, ?)", (username, password))
                conn.commit()
                messagebox.showinfo("Success", "Account created successfully!")
                self.show_login_page()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists")

    def logout(self):
        # Clean up resources
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        if self.timer_window is not None and self.timer_window.winfo_exists():
            self.timer_window.destroy()
            self.timer_window = None
        
        self.timer_running = False
        self.show_login_page()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def __del__(self):
        # Cleanup when the application is closed
        if self.cap is not None:
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = CubifierApp(root)
    root.mainloop()