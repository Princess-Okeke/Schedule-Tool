# Schedule_ttkbootstrap.py
import math
import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"
import tkinter as tk
from tkinter import simpledialog, colorchooser, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ttkbootstrap import Style, ttk

# -----------------------
# Theme / Colors / Config
# -----------------------
STYLE = "flatly"  # pick any ttkbootstrap theme you like (flatly, litera, darkly, solar, etc.)
FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 11, "bold")
BIG_BTN = {"width": 16, "padding": 8}  # used for large buttons
CANVAS_W = 420
CANVAS_H = 720

# default category colors
category_colors = {
    "Coursework": "#4fa3c7",
    "Sleep": "#b296c7",
    "Personal": "#f5a962",
    "Social": "#8fbc8f",
    "Recreation": "#ee6c6c"
}

# default activities (name -> (category, duration_hours))
default_activities = {
    "Take a Nap": ("Sleep", 1.0),
    "Eat Breakfast": ("Personal", 0.5),
    "Lift Weights": ("Recreation", 1.0),
    "TV with Friends": ("Social", 0.5),
    "Self Care": ("Personal", 1.0),
}

# schedule is a list of dicts: {day:'M'..'F', start:float, end:float, name:str, category:str, fixed:bool}
schedule = [
    # sample fixed entry
    {"day": "W", "start": 10.0, "end": 11.0, "name": "Writing Seminar", "category": "Coursework", "fixed": True},
    {"day": "W", "start": 12.0, "end": 13.0, "name": "Psychology Lecture", "category": "Coursework", "fixed": True},
]

reminders = [
    "Bring notes to Writing Seminar",
    "Email professor by 4 PM"
]

# helper: compute category totals from schedule
def compute_totals():
    totals = {k: 0.0 for k in category_colors.keys()}
    for e in schedule:
        cat = e.get("category", "Personal")
        dur = max(0.0, e["end"] - e["start"])
        totals[cat] = totals.get(cat, 0.0) + dur
    return totals

def format_time(h):
    h_int = int(h)
    m = int(round((h - h_int) * 60))
    suffix = "AM" if h_int < 12 else "PM"
    h_disp = h_int if 1 <= h_int <= 12 else (h_int - 12 if h_int > 12 else 12)
    return f"{h_disp}:{m:02d} {suffix}"

# -----------------------
# App
# -----------------------
class PlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Planner")
        self.style = Style(STYLE)
        self.selected_day = tk.StringVar(value="W")  # default day
        self.selected_schedule_item = None

        # Main layout frames
        main = ttk.Frame(root, padding=(12, 12, 12, 12))
        main.pack(fill="both", expand=True)

        left_col = ttk.Frame(main)
        left_col.grid(row=0, column=0, sticky="ns", padx=(0,12))

        center_col = ttk.Frame(main)
        center_col.grid(row=0, column=1, sticky="nsew", padx=(0,12))
        main.columnconfigure(1, weight=1)

        right_col = ttk.Frame(main)
        right_col.grid(row=0, column=2, sticky="ns")

        # ---------- LEFT: Activities & Categories ----------
        ttk.Label(left_col, text="Activities", font=FONT_BOLD).pack(anchor="w", pady=(0,8))

        self.act_list = tk.Listbox(left_col, width=28, height=16, font=FONT, activestyle='none', exportselection=False)
        self.act_list.pack()
        self.act_list.bind("<Double-Button-1>", lambda e: self.edit_activity())

        # big activity buttons (add / edit / remove)
        act_btn_frame = ttk.Frame(left_col)
        act_btn_frame.pack(fill="x", pady=(8,6))
        ttk.Button(act_btn_frame, text="Add Activity", bootstyle="primary", command=self.add_activity, **BIG_BTN).grid(row=0, column=0, padx=4, pady=4)
        ttk.Button(act_btn_frame, text="Edit Activity", bootstyle="secondary", command=self.edit_activity, **BIG_BTN).grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(act_btn_frame, text="Remove Activity", bootstyle="danger", command=self.remove_activity, **BIG_BTN).grid(row=1, column=0, padx=4, pady=4)
        ttk.Button(act_btn_frame, text="Edit Categories", bootstyle="info", command=self.edit_categories, **BIG_BTN).grid(row=1, column=1, padx=4, pady=4)

        # activity tiles preview (larger)
        ttk.Separator(left_col).pack(fill="x", pady=8)
        ttk.Label(left_col, text="Activity Tiles (click to add to schedule)", font=FONT_BOLD).pack(anchor="w", pady=(6,6))

        self.tile_frame = ttk.Frame(left_col)
        self.tile_frame.pack()
        self.build_tiles()

        # fill activity list
        self.refresh_activity_list()

        # ---------- CENTER: Time Grid Canvas + Day Selector + Controls ----------
        header_frame = ttk.Frame(center_col)
        header_frame.pack(fill="x", pady=(0,6))

        # Day selector
        days = ["M","T","W","Th","F","S","Su"]  # added Saturday and Sunday
        for idx, d in enumerate(days):
            b = ttk.Radiobutton(header_frame, text=d, value=d, variable=self.selected_day, command=self.redraw_canvas, bootstyle="secondary", width=5)
            b.grid(row=0, column=idx, padx=4)

        # Canvas
        canvas_frame = ttk.Frame(center_col)
        canvas_frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(canvas_frame, width=CANVAS_W, height=CANVAS_H, bg="white", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # legend / controls
        ctl_frame = ttk.Frame(center_col)
        ctl_frame.pack(fill="x", pady=(8,0))
        ttk.Button(ctl_frame, text="Add Fixed Activity", bootstyle="success", command=self.add_fixed_activity, **BIG_BTN).grid(row=0, column=0, padx=4, pady=4)
        ttk.Button(ctl_frame, text="Edit Selected", bootstyle="warning", command=self.edit_selected_schedule, **BIG_BTN).grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(ctl_frame, text="Remove Selected", bootstyle="danger", command=self.remove_selected_schedule, **BIG_BTN).grid(row=0, column=2, padx=4, pady=4)
        ttk.Button(ctl_frame, text="Clear Day", bootstyle="secondary", command=self.clear_day_schedule, **BIG_BTN).grid(row=0, column=3, padx=4, pady=4)

        # ---------- RIGHT: Schedule list + Reminders ----------
        ttk.Label(right_col, text="Schedule", font=FONT_BOLD).pack(anchor="w")
        self.schedule_list = tk.Listbox(right_col, width=36, height=16, font=FONT, activestyle='none', exportselection=False)
        self.schedule_list.pack()
        self.schedule_list.bind("<<ListboxSelect>>", self.on_schedule_select)
        self.schedule_list.bind("<Double-Button-1>", lambda e: self.edit_selected_schedule())

        # Reminders panel
        ttk.Separator(right_col).pack(fill="x", pady=8)
        ttk.Label(right_col, text="Reminders", font=FONT_BOLD).pack(anchor="w")
        self.rem_list = tk.Listbox(right_col, width=36, height=6, font=FONT, activestyle='none')
        self.rem_list.pack()
        rem_btn_f = ttk.Frame(right_col)
        rem_btn_f.pack(pady=(6,0))
        ttk.Button(rem_btn_f, text="Add", bootstyle="primary", command=self.add_reminder, width=10).grid(row=0, column=0, padx=4)
        ttk.Button(rem_btn_f, text="Edit", bootstyle="secondary", command=self.edit_reminder, width=10).grid(row=0, column=1, padx=4)
        ttk.Button(rem_btn_f, text="Remove", bootstyle="danger", command=self.remove_reminder, width=10).grid(row=0, column=2, padx=4)

        # ---------- BOTTOM: Donut Chart ----------
        donut_frame = ttk.Frame(right_col)
        donut_frame.pack(side="bottom", pady=(12,0), fill="both", expand=True)
        self.fig = plt.Figure(figsize=(4,2.8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=donut_frame)
        self.canvas_fig.get_tk_widget().pack(fill="both", expand=True)

        # initial population
        self.refresh_activity_list()
        self.refresh_schedule_list()
        self.refresh_reminders()
        self.draw_canvas()
        self.draw_donut()

    # -----------------------
    # Activity management
    # -----------------------
    def refresh_activity_list(self):
        self.act_list.delete(0, tk.END)
        for name, (cat, dur) in default_activities.items():
            self.act_list.insert(tk.END, f"{name} — {cat} • {dur}h")

    def add_activity(self):
        name = simpledialog.askstring("New Activity", "Activity name:")
        if not name:
            return
        if name in default_activities:
            messagebox.showerror("Exists", "Activity with that name already exists.")
            return
        category = simpledialog.askstring("Category", "Category (existing or new):")
        if not category:
            return
        duration = simpledialog.askfloat("Duration (hours)", "Duration in hours (e.g., 1 or 0.5):", initialvalue=1.0)
        if duration is None or duration <= 0:
            messagebox.showerror("Invalid", "Duration must be positive.")
            return
        default_activities[name] = (category, float(duration))
        # ensure category exists with color
        if category not in category_colors:
            color = colorchooser.askcolor(title=f"Pick color for new category '{category}'")[1]
            if not color:
                color = "#999999"
            category_colors[category] = color
        self.refresh_activity_list()
        self.build_tiles()

    def edit_activity(self):
        sel = self.act_list.curselection()
        if not sel:
            messagebox.showinfo("Select", "Double-click an activity or select and press Edit.")
            return
        idx = sel[0]
        name = list(default_activities.keys())[idx]
        cat, dur = default_activities[name]
        new_name = simpledialog.askstring("Edit Activity", "Name:", initialvalue=name)
        if not new_name:
            return
        new_cat = simpledialog.askstring("Category", "Category:", initialvalue=cat)
        if not new_cat:
            return
        new_dur = simpledialog.askfloat("Duration (hours)", "Duration:", initialvalue=dur)
        if new_dur is None or new_dur <= 0:
            messagebox.showerror("Invalid", "Duration must be positive.")
            return
        # handle rename
        if new_name != name:
            del default_activities[name]
        default_activities[new_name] = (new_cat, float(new_dur))
        if new_cat not in category_colors:
            color = colorchooser.askcolor(title=f"Pick color for new category '{new_cat}'")[1] or "#999999"
            category_colors[new_cat] = color
        self.refresh_activity_list()
        self.build_tiles()

    def remove_activity(self):
        sel = self.act_list.curselection()
        if not sel:
            messagebox.showinfo("Select", "Select an activity to remove.")
            return
        idx = sel[0]
        name = list(default_activities.keys())[idx]
        if messagebox.askyesno("Confirm", f"Remove activity '{name}'?"):
            del default_activities[name]
            self.refresh_activity_list()
            self.build_tiles()

    # tile builder: show activities as tappable tiles
    def build_tiles(self):
        for w in self.tile_frame.winfo_children():
            w.destroy()
        cols = 2
        idx = 0
        for name, (cat, dur) in default_activities.items():
            frm = ttk.Frame(self.tile_frame, width=200, height=60, style="card")  # wider & shorter
            frm.grid_propagate(False)
            frm.grid(row=idx//cols, column=idx%cols, padx=6, pady=6)
            lbl = ttk.Label(frm, text=name, font=FONT_BOLD)
            lbl.pack(anchor="w", padx=8, pady=(8,0), fill="x")
            sub = ttk.Label(frm, text=f"{cat} • {dur}h", font=FONT)
            sub.pack(anchor="w", padx=8, pady=(0,8), fill="x")
            frm.bind("<Button-1>", lambda e, nm=name: self.add_activity_to_day(nm))
            lbl.bind("<Button-1>", lambda e, nm=name: self.add_activity_to_day(nm))
            sub.bind("<Button-1>", lambda e, nm=name: self.add_activity_to_day(nm))
            idx += 1

    def add_activity_to_day(self, name):
        # adds activity to selected day at first available slot
        cat, dur = default_activities.get(name, ("Personal", 1.0))
        day = self.selected_day.get()
        start = 8.0
        found = False
        while start + dur <= 20.0:
            overlap = False
            for s in schedule:
                if s["day"] == day and not (start + dur <= s["start"] or start >= s["end"]):
                    overlap = True
                    break
            if not overlap:
                schedule.append({"day": day, "start": start, "end": start+dur, "name": name, "category": cat, "fixed": False})
                found = True
                break
            start += 0.5
        if not found:
            messagebox.showinfo("No space", "No available time slot to add that activity on this day.")
            return
        self.refresh_schedule_list()
        self.draw_canvas()
        self.draw_donut()

    # -----------------------
    # Schedule management
    # -----------------------
    def refresh_schedule_list(self):
        self.schedule_list.delete(0, tk.END)
        day = self.selected_day.get()
        day_entries = [e for e in schedule if e["day"] == day]
        day_entries = sorted(day_entries, key=lambda x: x["start"])
        for e in day_entries:
            fx = " (Fixed)" if e.get("fixed") else ""
            entry_text = f"{format_time(e['start'])} - {format_time(e['end'])}: {e['name']} — {e['category']}{fx}"
            self.schedule_list.insert(tk.END, entry_text)

    def on_schedule_select(self, event=None):
        sel = self.schedule_list.curselection()
        self.selected_schedule_item = None
        if not sel:
            return
        idx = sel[0]
        day = self.selected_day.get()
        day_entries = [e for e in schedule if e["day"] == day]
        day_entries = sorted(day_entries, key=lambda x: x["start"])
        if idx < len(day_entries):
            self.selected_schedule_item = day_entries[idx]

    def edit_selected_schedule(self):
        if not self.selected_schedule_item:
            messagebox.showinfo("Select", "Select a schedule item first (click it or pick from the list).")
            return
        e = self.selected_schedule_item
        name = simpledialog.askstring("Edit Name", "Name:", initialvalue=e["name"])
        if not name:
            return
        start = simpledialog.askfloat("Start (24h)", "Start time (e.g., 13.5):", initialvalue=e["start"])
        if start is None:
            return
        end = simpledialog.askfloat("End (24h)", "End time (must be > start):", initialvalue=e["end"])
        if end is None or end <= start:
            messagebox.showerror("Invalid", "End must be greater than start.")
            return
        cat = simpledialog.askstring("Category", "Category:", initialvalue=e.get("category", "Personal"))
        if not cat:
            return
        fixed = messagebox.askyesno("Fixed", "Should this be fixed (can't auto-move)?", icon="question")
        e.update({"name": name, "start": float(start), "end": float(end), "category": cat, "fixed": fixed})
        if cat not in category_colors:
            color = colorchooser.askcolor(title=f"Pick color for new category '{cat}'")[1] or "#999999"
            category_colors[cat] = color
        self.draw_canvas()
        self.refresh_schedule_list()
        self.draw_donut()

    def remove_selected_schedule(self):
        if not self.selected_schedule_item:
            messagebox.showinfo("Select", "Select a schedule item first.")
            return
        e = self.selected_schedule_item
        if messagebox.askyesno("Confirm", f"Remove '{e['name']}' from schedule?"):
            schedule.remove(e)
            self.selected_schedule_item = None
            self.draw_canvas()
            self.refresh_schedule_list()
            self.draw_donut()

    def clear_day_schedule(self):
        day = self.selected_day.get()
        if not messagebox.askyesno("Clear Day", f"Clear all schedule items for {day}?"):
            return
        global schedule
        schedule = [s for s in schedule if s["day"] != day]
        self.selected_schedule_item = None
        self.draw_canvas()
        self.refresh_schedule_list()
        self.draw_donut()

    def add_fixed_activity(self):
        name = simpledialog.askstring("Fixed Activity", "Name:")
        if not name:
            return
        start = simpledialog.askfloat("Start (24h)", "Start (e.g., 9.5 = 9:30 AM):")
        if start is None:
            return
        end = simpledialog.askfloat("End (24h)", "End (must be > start):")
        if end is None or end <= start:
            messagebox.showerror("Invalid", "End must be greater than start.")
            return
        day = simpledialog.askstring("Day", "Day code (M,T,W,Th,F):", initialvalue=self.selected_day.get())
        if not day:
            return
        category = simpledialog.askstring("Category", "Category (existing or new):", initialvalue=list(category_colors.keys())[0])
        if not category:
            return
        if category not in category_colors:
            color = colorchooser.askcolor(title=f"Pick color for new category '{category}'")[1] or "#999999"
            category_colors[category] = color
        schedule.append({"day": day, "start": float(start), "end": float(end), "name": name, "category": category, "fixed": True})
        self.draw_canvas()
        self.refresh_schedule_list()
        self.draw_donut()

    # -----------------------
    # Canvas: draw time grid & entries
    # -----------------------
    def draw_canvas(self):
        self.canvas.delete("all")
        # constants
        top_pad = 8
        left_label_w = 78
        hour_count = 12  # 8 AM - 8 PM
        hour_h = (CANVAS_H - 2 * top_pad) / hour_count
        # background
        self.canvas.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill="white", outline="")

        # hour rows & labels
        for i in range(hour_count):
            y1 = top_pad + i * hour_h
            y2 = y1 + hour_h
            self.canvas.create_line(left_label_w, y1, CANVAS_W, y1, fill="#e6e9ee")
            hour_label = 8 + i
            self.canvas.create_text(left_label_w/2, (y1 + y2)/2, text=format_time(hour_label), font=FONT)

        # right border line
        self.canvas.create_line(left_label_w, top_pad, left_label_w, CANVAS_H - top_pad, fill="#e6e9ee", width=1)

        # draw entries for selected day
        day = self.selected_day.get()
        day_entries = [e for e in schedule if e["day"] == day]
        day_entries = sorted(day_entries, key=lambda x: x["start"])
        for e in day_entries:
            s = max(8.0, e["start"])
            t = min(20.0, e["end"])
            if t <= 8.0 or s >= 20.0:
                continue
            y1 = top_pad + (s - 8.0) / hour_count * (CANVAS_H - 2*top_pad)
            y2 = top_pad + (t - 8.0) / hour_count * (CANVAS_H - 2*top_pad)
            c = category_colors.get(e.get("category"), "#999999")
            x1 = left_label_w + 8
            x2 = CANVAS_W - 12
            # rectangle (no radius param)
            rect_id = self.canvas.create_rectangle(x1, y1+3, x2, y2-3, fill=c, outline="#2b2b2b", width=0, tags=("entry",))
            text_x = x1 + 8
            self.canvas.create_text(text_x, (y1 + y2)/2, anchor="w", text=e["name"], font=FONT_BOLD, fill="#102030", tags=("entry",))
            dur_text = f"{max(0, e['end'] - e['start']):.1f}h"
            self.canvas.create_text(x2-28, (y1+y2)/2, text=dur_text, font=("Segoe UI", 9), fill="#fff", tags=("entry",))
            # store mapping on the rectangle tag for selection
            self.canvas.tag_bind(rect_id, "<Button-1>", lambda ev, ent=e: self.select_canvas_entry(ent))

        # footer note
        self.canvas.create_text(CANVAS_W/2, CANVAS_H-10, text=f"Day: {day} • Click a block to select/edit", font=("Segoe UI", 9), fill="#6c757d")

        # refresh schedule list
        self.refresh_schedule_list()

    def select_canvas_entry(self, ent):
        self.selected_schedule_item = ent
        messagebox.showinfo("Selected", f"Selected: {ent['name']} ({format_time(ent['start'])} - {format_time(ent['end'])})")

    def on_canvas_click(self, event):
        # quick-add at clicked time (snap to 30 min)
        left_label_w = 78
        if event.x < left_label_w:
            return
        top_pad = 8
        hour_count = 12
        if event.y < top_pad or event.y > CANVAS_H - top_pad:
            return
        frac = (event.y - top_pad) / (CANVAS_H - 2*top_pad)
        hour = 8.0 + frac * hour_count
        hour = round(hour * 2) / 2.0
        name = simpledialog.askstring("Quick Add", f"Name for new activity at {format_time(hour)}:")
        if not name:
            return
        duration = simpledialog.askfloat("Duration", "Duration in hours (e.g., 1 or 0.5):", initialvalue=1.0)
        if duration is None or duration <= 0:
            return
        day = self.selected_day.get()
        category = simpledialog.askstring("Category", "Category for this activity:", initialvalue="Personal")
        if category not in category_colors:
            color = colorchooser.askcolor(title=f"Pick color for new category '{category}'")[1] or "#999999"
            category_colors[category] = color
        schedule.append({"day": day, "start": hour, "end": hour + duration, "name": name, "category": category, "fixed": False})
        self.draw_canvas()
        self.draw_donut()

    # -----------------------
    # Reminders
    # -----------------------
    def refresh_reminders(self):
        self.rem_list.delete(0, tk.END)
        for r in reminders:
            self.rem_list.insert(tk.END, r)

    def add_reminder(self):
        txt = simpledialog.askstring("New Reminder", "Reminder text:")
        if txt:
            reminders.append(txt)
            self.refresh_reminders()

    def edit_reminder(self):
        sel = self.rem_list.curselection()
        if not sel:
            messagebox.showinfo("Select", "Select a reminder to edit.")
            return
        idx = sel[0]
        txt = simpledialog.askstring("Edit Reminder", "Reminder text:", initialvalue=reminders[idx])
        if txt:
            reminders[idx] = txt
            self.refresh_reminders()

    def remove_reminder(self):
        sel = self.rem_list.curselection()
        if not sel:
            messagebox.showinfo("Select", "Select a reminder to remove.")
            return
        idx = sel[0]
        if messagebox.askyesno("Confirm", "Remove selected reminder?"):
            reminders.pop(idx)
            self.refresh_reminders()

    # -----------------------
    # Categories editor
    # -----------------------
    def edit_categories(self):
        win = tk.Toplevel(self.root)
        win.title("Edit Categories")
        win.geometry("420x420")
        win.transient(self.root)

        lbl = ttk.Label(win, text="Categories", font=FONT_BOLD)
        lbl.pack(pady=(8,4))

        listbox = tk.Listbox(win, font=FONT, height=12)
        listbox.pack(fill="both", expand=True, padx=8)
        for k, v in category_colors.items():
            listbox.insert(tk.END, f"{k} — {v}")

        btnf = ttk.Frame(win)
        btnf.pack(pady=8)
        def add_cat():
            name = simpledialog.askstring("New Category", "Category name:")
            if not name:
                return
            color = colorchooser.askcolor(title="Pick category color")[1] or "#999999"
            category_colors[name] = color
            listbox.insert(tk.END, f"{name} — {color}")
            self.draw_canvas()
            self.draw_donut()

        def rename_cat():
            sel = listbox.curselection()
            if not sel:
                messagebox.showinfo("Select", "Select a category to rename.")
                return
            idx = sel[0]
            old = list(list(category_colors.keys()))[idx]
            new = simpledialog.askstring("Rename", "New name:", initialvalue=old)
            if not new:
                return
            color = category_colors.pop(old)
            category_colors[new] = color
            listbox.delete(idx)
            listbox.insert(idx, f"{new} — {color}")
            self.draw_canvas()
            self.draw_donut()

        def recolor_cat():
            sel = listbox.curselection()
            if not sel:
                messagebox.showinfo("Select", "Select a category to change color.")
                return
            idx = sel[0]
            name = list(list(category_colors.keys()))[idx]
            color = colorchooser.askcolor(title=f"Pick color for {name}")[1] or category_colors[name]
            category_colors[name] = color
            listbox.delete(idx)
            listbox.insert(idx, f"{name} — {color}")
            self.draw_canvas()
            self.draw_donut()

        def remove_cat():
            sel = listbox.curselection()
            if not sel:
                messagebox.showinfo("Select", "Select a category to remove.")
                return
            idx = sel[0]
            name = list(list(category_colors.keys()))[idx]
            if messagebox.askyesno("Confirm", f"Remove category '{name}'? This will NOT remove scheduled items but they may show default colors."):
                del category_colors[name]
                listbox.delete(idx)
                self.draw_canvas()
                self.draw_donut()

        ttk.Button(btnf, text="Add", bootstyle="success", command=add_cat).grid(row=0, column=0, padx=6)
        ttk.Button(btnf, text="Rename", bootstyle="secondary", command=rename_cat).grid(row=0, column=1, padx=6)
        ttk.Button(btnf, text="Recolor", bootstyle="info", command=recolor_cat).grid(row=0, column=2, padx=6)
        ttk.Button(btnf, text="Remove", bootstyle="danger", command=remove_cat).grid(row=0, column=3, padx=6)

    # -----------------------
    # Donut chart
    # -----------------------
    def draw_donut(self):
        self.ax.clear()
        totals = compute_totals()
        labels = []
        sizes = []
        colors = []
        for k, v in totals.items():
            if v > 0:
                labels.append(k)
                sizes.append(v)
                colors.append(category_colors.get(k, "#999999"))
        if not sizes:
            # placeholder segments to keep look pleasant
            labels = list(category_colors.keys())[:3]
            sizes = [1, 1, 1]
            colors = [category_colors[k] for k in labels]
    
        # Add percentages around donut
        wedges, texts, autotexts = self.ax.pie(
            sizes, colors=colors, radius=1.0,
            wedgeprops=dict(width=0.4, edgecolor='white'),
            labels=labels,
            autopct=lambda pct: f"{pct:.1f}% ({pct*sum(sizes)/100:.1f}h)",  # shows both % and hours
            textprops=dict(color="black", fontsize=9)
        )
    
        self.ax.set_aspect("equal")
        self.ax.text(0, 0, "Hours\nAllocated", ha="center", va="center", fontsize=10, fontweight="bold")
        self.fig.tight_layout()
        self.canvas_fig.draw()


    # -----------------------
    # Helpers to refresh
    # -----------------------
    def redraw_canvas(self):
        self.draw_canvas()
        self.refresh_schedule_list()

# -----------------------
# Run App
# -----------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = PlannerApp(root)
    root.geometry("1280x880")
    root.mainloop()
