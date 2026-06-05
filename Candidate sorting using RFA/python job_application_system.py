import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder
from datetime import datetime

# Constants
JOB_ROLES = ["Web Developer", "Project Manager", "Business Analyst", "HR Specialist",
             "Data Scientist", "UX Designer", "DevOps Engineer", "Marketing Manager",
             "Financial Analyst", "Sales Executive"]
BG_COLOR, HEADER_COLOR, BUTTON_COLOR = "#ffffff", "#e8f5e9", "#4CAF50"
TEXT_COLOR, ACCENT_COLOR, ERROR_COLOR = "#333333", "#2E7D32", "#f44336"
ENTRY_BG = "#f5f5f5"

def load_dataset(csv_file="job_descriptions.csv"):
    if not os.path.exists(csv_file):
        messagebox.showerror("Error", f"Dataset file {csv_file} not found!")
        exit()
    
    df = pd.read_csv(csv_file)
    
    required_cols = ['Name', 'Age', 'Gender', 'EdLevel', 'YearsCode', 'YearsCodePro',
                    'Country', 'PreviousSalary', 'HaveWorkedWith', 'ComputerSkills',
                    'MentalHealth', 'Employed', 'Username', 'Password', 'JobRole']
    
    for col in required_cols:
        if col not in df.columns:
            if col == 'Username':
                df['Username'] = [f"{str(n).split()[0].lower()}{str(n).split()[1].lower()}" for n in df['Name']]
            elif col == 'Password':
                df['Password'] = [f"{str(n).split()[0].lower()}{str(n).split()[1].lower()}123" for n in df['Name']]
            elif col == 'JobRole':
                df['JobRole'] = np.random.choice(JOB_ROLES, len(df))
            elif col in ['Status', 'Feedback']:
                df[col] = "" if col == 'Feedback' else "Pending"
            elif col == 'ApplicationDate':
                df[col] = datetime.now().strftime("%Y-%m-%d")
            else:
                df[col] = np.nan
    
    return df

df = load_dataset()

def save_dataset():
    df.to_csv("job_descriptions.csv", index=False)

# Encoders
for col, encoder in [('EdLevel', LabelEncoder()), ('Country', LabelEncoder()),
                    ('HaveWorkedWith', LabelEncoder()), ('Gender', LabelEncoder()),
                    ('JobRole', LabelEncoder())]:
    df[f'{col}_enc'] = encoder.fit_transform(df[col])

def calculate_priority(row):
    score = 0
    if row['EdLevel'] == "PhD": score += 30
    elif row['EdLevel'] == "Master": score += 20
    elif row['EdLevel'] == "Bachelor": score += 10
    score += row['YearsCodePro'] * 2 + row['ComputerSkills'] * 3
    if row['MentalHealth'] == "Good": score += 15
    elif row['MentalHealth'] == "Fair": score += 5
    if row['JobRole'] in ["Web Developer", "Data Scientist", "DevOps Engineer"]: score += 25
    elif row['JobRole'] in ["Project Manager", "Business Analyst"]: score += 15
    return score

df['PriorityScore'] = df.apply(calculate_priority, axis=1)
credentials = dict(zip(df['Username'], df['Password']))
credentials["admin"] = "admin123"

class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Application Portal - Login")
        self.root.geometry("500x500")
        self.root.configure(bg=BG_COLOR)
        self.root.eval('tk::PlaceWindow . center')
        
        self.title_font = ("Bahnschrift SemiBold", 24, "bold")
        self.label_font = ("Bahnschrift SemiBold", 12)
        
        tk.Frame(root, bg=HEADER_COLOR, height=50).pack(fill=tk.X, side=tk.TOP)
        tk.Frame(root, bg=HEADER_COLOR, height=50).pack(fill=tk.X, side=tk.BOTTOM)
        
        main_frame = tk.Frame(root, bg=BG_COLOR)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)
        
        tk.Label(main_frame, text="Welcome to Job Application Portal", 
                font=self.title_font, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(0, 30))
        
        for label_text, entry_var in [("Username:", "username_entry"), ("Password:", "password_entry")]:
            tk.Label(main_frame, text=label_text, font=self.label_font, bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor="center")
            entry = tk.Entry(main_frame, font=self.label_font, bg=ENTRY_BG, fg=TEXT_COLOR, 
                            relief=tk.GROOVE, borderwidth=2, width=25)
            if label_text == "Password:": entry.config(show="*")
            entry.pack(pady=10, ipady=8)
            setattr(self, entry_var, entry)
        
        button_frame = tk.Frame(main_frame, bg=BG_COLOR)
        button_frame.pack(pady=20)
        
        for text, cmd in [("Admin Login", self.admin_login), ("User Login", self.user_login), 
                         ("Register", self.register)]:
            tk.Button(button_frame, text=text, command=cmd, font=self.label_font, 
                     bg=BUTTON_COLOR, fg="white", relief=tk.RAISED, bd=2, padx=15, pady=5).pack(fill=tk.X, pady=5)
    
    def admin_login(self):
        if self.username_entry.get() == "admin" and self.password_entry.get() == "admin123":
            self.root.destroy()
            root = tk.Tk()
            AdminDashboard(root)
            root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid Admin Credentials")
    
    def user_login(self):
        username, password = self.username_entry.get().strip().lower(), self.password_entry.get().strip()
        if username in credentials:
            if credentials[username] == password:
                self.root.destroy()
                root = tk.Tk()
                UserDashboard(root, username)
                root.mainloop()
            else:
                messagebox.showerror("Error", f"Wrong password for {username}\nCorrect format: username123")
        else:
            messagebox.showerror("Error", "Username not found or not authorized to login")
    
    def register(self):
        messagebox.showinfo("Info", "All candidates are pre-registered in the system!")

class AdminDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Recruiter Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg=BG_COLOR)
        
        self.title_font = ("Bahnschrift SemiBold", 24, "bold")
        self.label_font = ("Bahnschrift SemiBold", 14)
        
        tk.Frame(root, bg=HEADER_COLOR, height=50).pack(fill=tk.X, side=tk.TOP)
        tk.Frame(root, bg=HEADER_COLOR, height=50).pack(fill=tk.X, side=tk.BOTTOM)
        
        self.sorted_df = df.sort_values('PriorityScore', ascending=False)
        main_frame = tk.Frame(root, bg=BG_COLOR)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        tk.Label(main_frame, text="Recruiter Dashboard", 
                font=self.title_font, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
        
        filter_frame = tk.Frame(main_frame, bg=BG_COLOR)
        filter_frame.pack(pady=10)
        
        for label, var, values in [("Filter by Status:", "status_var", ["All", "Pending", "Approved", "Rejected"]), 
                                 ("Filter by Job Role:", "jobrole_var", ["All"] + JOB_ROLES)]:
            tk.Label(filter_frame, text=label, font=self.label_font, bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)
            setattr(self, var, tk.StringVar(value="All"))
            cb = ttk.Combobox(filter_frame, textvariable=getattr(self, var), values=values, 
                             font=self.label_font, state="readonly")
            cb.pack(side=tk.LEFT, padx=10)
            cb.bind("<<ComboboxSelected>>", self.filter_candidates)
        
        tree_frame = tk.Frame(main_frame, bg=BG_COLOR)
        tree_frame.pack(expand=True, fill=tk.BOTH, pady=10)
        
        self.tree_scroll = tk.Scrollbar(tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.candidate_tree = ttk.Treeview(tree_frame, yscrollcommand=self.tree_scroll.set, selectmode="browse",
                                         columns=("Name", "Age", "Job Role", "Experience", "Status", "Priority"), show="headings")
        self.tree_scroll.config(command=self.candidate_tree.yview)
        
        for col, width in [("Name", 200), ("Age", 60), ("Job Role", 150), 
                          ("Experience", 100), ("Status", 100), ("Priority", 80)]:
            self.candidate_tree.column(col, width=width, anchor=tk.CENTER)
            self.candidate_tree.heading(col, text=col)
        
        self.populate_treeview()
        self.candidate_tree.pack(expand=True, fill=tk.BOTH)
        
        button_frame = tk.Frame(main_frame, bg=BG_COLOR)
        button_frame.pack(pady=10)
        
        for text, cmd in [("View Details", self.view_details), 
                         ("Approve", lambda: self.update_status("Approved")),
                         ("Reject", lambda: self.update_status("Rejected")), 
                         ("Add Feedback", self.add_feedback),
                         ("Export Data", self.export_data), 
                         ("Logout", self.logout)]:
            color = BUTTON_COLOR if text != "Logout" else ERROR_COLOR
            tk.Button(button_frame, text=text, command=cmd, font=self.label_font, 
                     bg=color, fg="white", relief=tk.RAISED, bd=2).pack(side=tk.LEFT, padx=5)
    
    def populate_treeview(self, status_filter="All", jobrole_filter="All"):
        self.candidate_tree.delete(*self.candidate_tree.get_children())
        filtered_df = self.sorted_df
        if status_filter != "All": 
            filtered_df = filtered_df[filtered_df['Status'] == status_filter]
        if jobrole_filter != "All": 
            filtered_df = filtered_df[filtered_df['JobRole'] == jobrole_filter]
        for _, row in filtered_df.iterrows():
            self.candidate_tree.insert("", tk.END, values=(
                row['Name'], row['Age'], row['JobRole'], 
                f"{row['YearsCodePro']} yrs", row['Status'], row['PriorityScore']
            ))
    
    def filter_candidates(self, event=None): 
        self.populate_treeview(self.status_var.get(), self.jobrole_var.get())
    
    def get_selected_candidate(self):
        try:
            selected_item = self.candidate_tree.selection()[0]
            return df[df['Name'] == self.candidate_tree.item(selected_item)['values'][0]].index[0]
        except:
            messagebox.showwarning("Warning", "Please select a candidate first")
            return None
    
    def view_details(self):
        selected_index = self.get_selected_candidate()
        if selected_index is None: return
        
        candidate = df.iloc[selected_index]
        details_window = tk.Toplevel(self.root)
        details_window.title("Candidate Details")
        details_window.geometry("600x500")
        details_window.configure(bg=BG_COLOR)
        
        tk.Label(details_window, text=candidate['Name'], 
                font=self.title_font, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
        
        details_frame = tk.Frame(details_window, bg=BG_COLOR)
        details_frame.pack(expand=True, fill=tk.BOTH, padx=20)
        
        for frame_side, labels in [
            (tk.LEFT, [
                f"Age: {candidate['Age']}", 
                f"Gender: {candidate['Gender']}", 
                f"Education: {candidate['EdLevel']}", 
                f"Job Role: {candidate['JobRole']}", 
                f"Country: {candidate['Country']}"
            ]),
            (tk.LEFT, [
                f"Professional Exp: {candidate['YearsCodePro']} yrs", 
                f"Skills: {candidate['HaveWorkedWith']}", 
                f"Computer Skills: {candidate['ComputerSkills']}/10", 
                f"Mental Health: {candidate['MentalHealth']}", 
                f"Status: {candidate['Status']}"
            ])
        ]:
            frame = tk.Frame(details_frame, bg=BG_COLOR)
            frame.pack(side=frame_side, fill=tk.BOTH, expand=True, padx=20)
            for label in labels: 
                tk.Label(frame, text=label, font=self.label_font, 
                        bg=BG_COLOR, fg=TEXT_COLOR, anchor="w").pack(fill=tk.X, pady=5)
        
        tk.Label(details_window, text=f"Priority Score: {candidate['PriorityScore']}", 
                font=self.label_font, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
        
        if candidate['Status'] == "Rejected":
            feedback_frame = tk.Frame(details_window, bg=BG_COLOR)
            feedback_frame.pack(fill=tk.X, padx=20, pady=10)
            tk.Label(feedback_frame, text="Feedback:", 
                    font=self.label_font, bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor="w")
            feedback_text = tk.Text(feedback_frame, height=5, width=60, wrap=tk.WORD, 
                                  font=self.label_font, bg="white", fg=TEXT_COLOR)
            feedback_text.insert(tk.END, candidate['Feedback'])
            feedback_text.config(state=tk.DISABLED)
            feedback_text.pack(fill=tk.X)
    
    def update_status(self, new_status):
        selected_index = self.get_selected_candidate()
        if selected_index is None: return
        
        df.at[selected_index, 'Status'] = new_status
        save_dataset()
        self.populate_treeview(self.status_var.get(), self.jobrole_var.get())
        
        popup = tk.Toplevel(self.root)
        popup.title("Status Updated")
        popup.geometry("400x200")
        popup.configure(bg=BG_COLOR)
        
        color = ACCENT_COLOR if new_status == "Approved" else ERROR_COLOR
        tk.Label(popup, text=new_status.upper() + "!", 
                font=("Arial", 36), bg=BG_COLOR, fg=color).pack(expand=True)
        tk.Button(popup, text="OK", command=popup.destroy,
                font=self.label_font, bg=BUTTON_COLOR, fg="white").pack(pady=10)
    
    def add_feedback(self):
        selected_index = self.get_selected_candidate()
        if selected_index is None: return
        if df.at[selected_index, 'Status'] != "Rejected":
            messagebox.showwarning("Warning", "Feedback can only be added for rejected candidates!")
            return
        
        feedback = simpledialog.askstring("Add Feedback", "Enter feedback for this candidate:")
        if feedback:
            df.at[selected_index, 'Feedback'] = feedback
            save_dataset()
            messagebox.showinfo("Success", "Feedback added successfully")
    
    def export_data(self):
        status, jobrole = self.status_var.get(), self.jobrole_var.get()
        filtered_df = df
        if status != "All": 
            filtered_df = filtered_df[filtered_df['Status'] == status]
        if jobrole != "All": 
            filtered_df = filtered_df[filtered_df['JobRole'] == jobrole]
        
        filename = f"candidates_{status.lower() if status != 'All' else 'all'}"
        if jobrole != "All": 
            filename += f"_{jobrole.lower().replace(' ', '')}"
        filename += ".csv"
        
        filtered_df.to_csv(filename, index=False)
        messagebox.showinfo("Export Complete", f"Data exported to:\n{os.path.abspath(filename)}")
    
    def logout(self):
        self.root.destroy()
        root = tk.Tk()
        LoginPage(root)
        root.mainloop()

class UserDashboard:
    def __init__(self, root, username):
        self.root, self.username = root, username
        self.user_data = df[df['Username'] == username].iloc[0]
        
        self.root.title("User Dashboard")
        self.root.geometry("900x700")
        self.root.configure(bg=BG_COLOR)
        
        self.title_font = ("Bahnschrift SemiBold", 24, "bold")
        self.header_font = ("Bahnschrift SemiBold", 16, "bold")
        self.label_font = ("Bahnschrift SemiBold", 12)
        
        tk.Frame(root, bg=HEADER_COLOR, height=50).pack(fill=tk.X, side=tk.TOP)
        tk.Frame(root, bg=HEADER_COLOR, height=50).pack(fill=tk.X, side=tk.BOTTOM)
        
        self.canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_COLOR)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        center_container = tk.Frame(self.scrollable_frame, bg=BG_COLOR)
        center_container.pack(expand=True, fill=tk.BOTH, padx=50, pady=20)
        
        tk.Label(center_container, text="User Dashboard", 
                font=self.title_font, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(0, 20))
        
        status_frame = tk.Frame(center_container, bg=BUTTON_COLOR, bd=2, relief=tk.RAISED)
        status_frame.pack(fill=tk.X, pady=10)
        tk.Label(status_frame, text=f"Application Status: {self.user_data['Status'].upper()}", 
                font=self.header_font, bg=BUTTON_COLOR, fg="white").pack(pady=10)
        
        job_frame = tk.Frame(center_container, bg=HEADER_COLOR, bd=2, relief=tk.GROOVE)
        job_frame.pack(fill=tk.X, pady=10)
        tk.Label(job_frame, text=f"Applied Position: {self.user_data['JobRole']}", 
                font=self.header_font, bg=HEADER_COLOR, fg=TEXT_COLOR).pack(pady=5)
        
        details_frame = tk.Frame(center_container, bg=BG_COLOR)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        for frame_side, labels in [
            (tk.LEFT, [
                f"Name: {self.user_data['Name']}", 
                f"Age: {self.user_data['Age']}", 
                f"Gender: {self.user_data['Gender']}", 
                f"Education: {self.user_data['EdLevel']}", 
                f"Country: {self.user_data['Country']}"
            ]),
            (tk.LEFT, [
                f"Professional Exp: {self.user_data['YearsCodePro']} yrs", 
                f"Total Coding Exp: {self.user_data['YearsCode']} yrs", 
                f"Skills: {self.user_data['HaveWorkedWith']}", 
                f"Computer Skills: {self.user_data['ComputerSkills']}/10", 
                f"Mental Health: {self.user_data['MentalHealth']}"
            ])
        ]:
            frame = tk.Frame(details_frame, bg=BG_COLOR)
            frame.pack(side=frame_side, fill=tk.BOTH, expand=True, padx=20)
            for label in labels: 
                tk.Label(frame, text=label, font=self.label_font, 
                        bg=BG_COLOR, fg=TEXT_COLOR, anchor="w").pack(fill=tk.X, pady=5)
        
        tk.Label(center_container, text=f"Priority Score: {self.user_data['PriorityScore']}", 
                font=self.label_font, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
        
        button_frame = tk.Frame(center_container, bg=BG_COLOR)
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Check Detailed Status", command=self.show_status, 
                font=self.header_font, bg=BUTTON_COLOR, fg="white", relief=tk.RAISED, bd=3).pack()
        
        logout_frame = tk.Frame(self.scrollable_frame, bg=HEADER_COLOR)
        logout_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        tk.Button(logout_frame, text="LOGOUT", command=self.logout,
                font=self.header_font, bg=ERROR_COLOR, fg="white", padx=20).pack()
    
    def show_status(self):
        status, feedback, job_role = self.user_data['Status'], self.user_data['Feedback'], self.user_data['JobRole']
        popup = tk.Toplevel(self.root)
        popup.title("Application Status Details")
        popup.geometry("600x400")
        popup.configure(bg=BG_COLOR)
        
        main_frame = tk.Frame(popup, bg=BG_COLOR)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        tk.Label(main_frame, text=f"Position Applied: {job_role}", 
            font=self.header_font, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
        
        if status == "Approved":
            tk.Label(main_frame, text="CONGRATULATIONS!", 
                    font=("Arial", 12), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=20)
            tk.Label(main_frame, text="Your application has been approved!",
                font=self.label_font, bg=BG_COLOR, fg=TEXT_COLOR).pack()
        elif status == "Rejected":
            tk.Label(main_frame, text="APPLICATION DECLINED", 
                    font=("Arial", 12), bg=BG_COLOR, fg=ERROR_COLOR).pack(pady=10)
            
            feedback_frame = tk.Frame(main_frame, bg="#FFEBEE", bd=2, relief=tk.GROOVE)
            feedback_frame.pack(fill=tk.X, pady=10, padx=10)
            
            tk.Label(feedback_frame, text="Feedback from the recruiter:",
                font=self.header_font, bg="#FFEBEE", fg=TEXT_COLOR).pack(pady=5, anchor="w")
            
            feedback_text = tk.Text(feedback_frame, height=8, width=50, wrap=tk.WORD,
                                font=self.label_font, bg="#FFEBEE", fg=TEXT_COLOR, bd=0)
            feedback_text.insert(tk.END, feedback)
            feedback_text.config(state=tk.DISABLED)
            feedback_text.pack(padx=10, pady=5, fill=tk.BOTH)
        else:
            tk.Label(main_frame, text="Your application is being reviewed", 
                    font=("Arial", 12), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
            tk.Label(main_frame, text="We appreciate your patience!",
                font=("Arial", 10), bg=BG_COLOR, fg=TEXT_COLOR).pack()
        
        tk.Button(main_frame, text="CLOSE", command=popup.destroy,
                font=self.header_font, bg=BUTTON_COLOR, fg="white").pack(pady=20)
    
    def logout(self):
        self.root.destroy()
        root = tk.Tk()
        LoginPage(root)
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    LoginPage(root)
    root.mainloop()