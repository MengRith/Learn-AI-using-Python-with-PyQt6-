import requests
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# API base URL (adjust to your API project's URL)
BASE_URL = "http://localhost:5204/api/tsheet" # Update port based on your API project's launchSe2ngs.json
class TimeSheetClient: 
    def __init__(self, root): 
        self.root = root 
        self.root.title("Employee TimeSheet Client") 
        tk.Label(root, text="Employee ID:").grid(row=0, column=0, padx=5, pady=5) 
        self.employee_id_entry = tk.Entry(root) 
        self.employee_id_entry.grid(row=0, column=1, padx=5, pady=5) 
        tk.Button(root, text="Time In", command=self.time_in).grid(row=1, column=0, padx=5, pady=5) 
        tk.Button(root, text="Time Out", command=self.time_out).grid(row=1, column=1, padx=5, pady=5) 
        tk.Button(root, text="View TimeSheets", command=self.view_timesheets).grid(row=2, column=0, columnspan=2, pady=5) 
        self.output = tk.Text(root, height=10, width=50) 
        self.output.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        self.current_timesheet_id = None

    def time_in(self):
        self.output.delete(1.0, tk.END)
        employee_id = self.employee_id_entry.get()
        if not employee_id.isdigit():
            messagebox.showerror("Error", "Enter a valid Employee ID")
            return
        response = requests.post(f"{BASE_URL}/timein/{employee_id}")
        if response.status_code == 201:
            data = response.json()
            self.current_timesheet_id = data["id"]
            name = data.get("employeeName", "Unknown")
            self.output.insert(tk.END, f"{name} Timed In at {data['timeIn']}\n")
        else:
            self.output.insert(tk.END, f"Error: {response.text}\n")

    def time_out(self):
        if not self.current_timesheet_id: 
            messagebox.showerror("Error", "No active TimeSheet to time out") 
            return 
        response = requests.post(f"{BASE_URL}/timeout/{self.current_timesheet_id}") 
        if response.status_code == 200: 
            data = response.json() 
            self.output.insert(tk.END, f"Timed Out at {data['timeOut']}\n") 
            self.current_timesheet_id = None
        else: self.output.insert(tk.END,f"Error: {response.text}\n")

    def view_timesheets(self):
        response = requests.get(BASE_URL) 
        if response.status_code == 200: 
            timesheets = response.json() 
            self.output.delete(1.0, tk.END) 
            for ts in timesheets: 
                self.output.insert(tk.END, f"ID: {ts['id']}, Employee: {ts['employeeId']}, " 
                                   f"In: {ts['timeIn']}, Out: {ts['timeOut']}\n") 
        else: self.output.insert(tk.END, f"Error: {response.text}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeSheetClient(root)
    root.mainloop()