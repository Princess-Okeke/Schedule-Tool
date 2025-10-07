# Daily Planner Desktop App

## Overview
**Daily Planner** is a desktop application built in Python for users to visually manage and analyze their daily schedules. The app features an interactive time grid, customizable activities, and real-time data visualization to enhance personal productivity and time management. 

It provides a modern, intuitive interface for organizing tasks and gaining insights into how time is allocated across various life categories.


## App Demo


https://github.com/user-attachments/assets/9eddf2af-b0fa-49b2-90b2-a27ecf272c0f


<img width="330" height="220" alt="Screenshot 2025-10-06 at 4 47 15 PM" src="https://github.com/user-attachments/assets/f2bd8cfc-0d9e-41ba-909a-070b2e87ffe0" />
<img width="330" height="220" alt="Screenshot 2025-10-06 at 5 02 00 PM" src="https://github.com/user-attachments/assets/4fac4f80-7bee-43f1-a5ac-1ad27b7bc3cb" />
<img width="330" height="220" alt="Screenshot 2025-10-06 at 5 02 40 PM" src="https://github.com/user-attachments/assets/ca45df6a-5092-4e01-9f42-5339928c637e" />





## App Features

- **Interactive Time Grid**: Visually schedule activities in a 12-hour day view (8 AM - 8 PM) across a full 7-day week.
- **Dynamic Scheduling**: Add both fixed events (e.g., classes) and flexible activities. Quickly add new tasks by clicking on activity tiles or directly onto an open time slot on the canvas.
- **Customizable Activities & Categories**: Create, edit, and remove activities with custom durations. Organize activities into categories with user-selectable colors for easy visual identification.
- **Data Visualization**: A real-time **Matplotlib** donut chart displays the percentage and total hours allocated to each category, providing instant insights into time usage.
- **Reminder System**: An integrated list allows users to add, edit, and remove simple text reminders to keep track of important to-dos.
- **Modern UI**: A clean, professionally themed interface built using the **ttkbootstrap** library for an enhanced user experience.



## Technology Implemented

1.  **Tkinter**
    - Python’s standard GUI (Graphical User Interface) library, used to build the core application window, canvas, buttons, and dialog boxes.
2.  **ttkbootstrap**
    - A modern theme library for Tkinter that provides a collection of professionally styled widgets and a simple API for creating visually appealing user interfaces.
3.  **Matplotlib**
    - A powerful data visualization and plotting library for Python. In this app, it's used to create and embed the dynamic "Hours Allocated" donut chart for schedule analysis.



## How to Clone and Run

### Prerequisites
- Install **Python 3.x**: [Download here](https://www.python.org/downloads/).
- Install **required libraries**:

```bash
pip install ttkbootstrap matplotlib
```

### Clone the Repository
- Open your terminal.
- Navigate to your desired directory.
- Run:

```bash
git clone <YOUR_REPOSITORY_URL_HERE>
```

### Run the Application
- Change into the cloned directory:

```bash
cd <YOUR_REPOSITORY_FOLDER_NAME>
```
- Execute the script:
```bash
python3 Schedule_ttkbootstrap.py
```
**Notes:**
- Ensure Tkinter is included with your Python installation (it's standard with most Python distributions).
- Follow the on-screen prompts to manage your schedule!



## Conclusion
The **Daily Planner** app combines a user-friendly, event-driven interface with powerful scheduling and data visualization features. It serves as a comprehensive tool for personal time management, helping users organize their days and analyze their productivity at a glance.

