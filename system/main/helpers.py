import tkinter as tk
import platform  
import calendar
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from datetime import date, datetime
# Mohamed Hamouda (23077543)
# Momchil Georgiev (24033989)
# -------------------------------------------------------
# Constants
# -------------------------------------------------------
BG         = "white"
ACCENT     = "#E53935"
BTN_FG     = "white"
FONT_TITLE = ("Arial", 20, "bold")
FONT_LABEL = ("Arial", 12)
FONT_ENTRY = ("Arial", 12)
FONT_BTN   = ("Arial", 12, "bold")
ENTRY_H    = 36
ENTRY_W    = 28
RADIUS     = 6
NAV_BG     = BG          
APP_BG     = '#c9e4c4'
NAV_BTN    = "#3B86FF"


# -------------------------------------------------------
# Core Widgets
# -------------------------------------------------------

def create_button(parent, text="Click Me", width=150, height=50, bg="red", fg=BTN_FG,
                  command=None, x=None, y=None, next_window_func=None, current_window=None,
                  auto_pack=True, state="normal"):
    """Improved styled canvas button with persistent hover states."""
    button_font = ("Arial", 14, "bold")
    measured_width = tkfont.Font(font=button_font).measure(text) + 36
    width = max(width, measured_width)

    def on_click(event=None):
        if getattr(canvas, "_button_state", "normal") == "disabled":
            return
        if command:
            command()
        if next_window_func and current_window:
            current_window.destroy()
            next_window_func()

    parent_bg = parent.cget("bg") if hasattr(parent, "cget") else BG
    canvas = tk.Canvas(parent, width=width, height=height, highlightthickness=0, bd=0, bg=parent_bg)

    canvas.base_color = bg
    canvas.text_color = fg
    canvas._button_state = state

    if x is not None and y is not None:
        canvas.place(x=x, y=y)
    elif auto_pack:
        canvas.pack(fill="x", expand=True, pady=5)

    canvas.create_rectangle(0, 0, width, height, fill=bg, outline=bg, tags="rect")
    canvas.create_text(width // 2, height // 2, text=text, fill=fg, font=button_font, tags="text")

    original_config = canvas.config

    def _config(*args, **kwargs):
        forwarded_kwargs = dict(kwargs)
        if kwargs:
            if "bg" in kwargs:
                canvas.base_color = kwargs["bg"]
                canvas.itemconfig("rect", fill=canvas.base_color, outline=canvas.base_color)
                forwarded_kwargs.pop("bg", None)
            if "fg" in kwargs:
                canvas.text_color = kwargs["fg"]
                canvas.itemconfig("text", fill=canvas.text_color)
                forwarded_kwargs.pop("fg", None)
            if "text" in kwargs:
                canvas.itemconfig("text", text=kwargs["text"])
                forwarded_kwargs.pop("text", None)
            if "state" in kwargs:
                canvas._button_state = kwargs["state"]
                forwarded_kwargs.pop("state", None)
        return original_config(*args, **forwarded_kwargs)

    canvas.config = _config
    canvas.configure = _config

    def on_enter(e):
        if canvas._button_state == "disabled":
            return
        if canvas.base_color in ("white", NAV_BG):
            h_color = "#dbeafe"   # more visible than #f0f0f0
        elif canvas.base_color in ("red", "#E53935"):
            h_color = "#cc0000"
        elif canvas.base_color == NAV_BTN:
            h_color = "#2a62c9"
        else:
            h_color = canvas.base_color
        canvas.itemconfig("rect", fill=h_color, outline=h_color)

    def on_leave(e):
        canvas.itemconfig("rect", fill=canvas.base_color, outline=canvas.base_color)

    canvas.tag_bind("rect", "<Button-1>", on_click)
    canvas.tag_bind("text", "<Button-1>", on_click)

    canvas.tag_bind("rect", "<Enter>", on_enter)
    canvas.tag_bind("text", "<Enter>", on_enter)
    canvas.tag_bind("rect", "<Leave>", on_leave)
    canvas.tag_bind("text", "<Leave>", on_leave)

    return canvas

def create_window(title):
    root = tk.Tk()
    root.title(title)
    root.geometry("750x650")
    root.minsize(750, 650)
    root.configure(bg=APP_BG)
    return root


def create_frame(parent):
    frame = tk.Frame(parent, bg=APP_BG)
    top_btn_frame = tk.Frame(frame, bg=APP_BG)
    top_btn_frame.pack(side="top", fill="x", pady=(30, 10))
    btns_inner_frame = tk.Frame(top_btn_frame, bg=APP_BG)
    btns_inner_frame.pack(anchor="center")
    box_frame = tk.Frame(frame, bg=APP_BG)
    box_frame.pack(fill="both", expand=True, padx=40, pady=(10, 40))
    return frame, btns_inner_frame, box_frame


def clear_frame(frame):
    """Remove all widgets inside a given frame."""
    for widget in frame.winfo_children():
        widget.destroy()


# -------------------------------------------------------
# Navigation
# -------------------------------------------------------

def _nav_frame(parent, bg=NAV_BG, **pack_kwargs):
    """Shared helper: creates a white sub-frame inside a navbar."""
    f = tk.Frame(parent, bg=bg)
    f.pack(**pack_kwargs)
    return f


def create_navbar(parent, logo_path, button_text, button_command=None):
    frame = tk.Frame(parent, bg=NAV_BG, height=120)
    frame.pack(fill="x", padx=0, pady=(0, 30))
    frame.pack_propagate(False)

    left_frame = _nav_frame(frame, side="left", padx=20, pady=20)
    frame.logo_image = tk.PhotoImage(master=frame, file=logo_path).subsample(2, 2)
    tk.Label(left_frame, image=frame.logo_image, bg=NAV_BG).pack(side="left")

    center_frame = _nav_frame(frame, side="left", expand=True)
    tk.Label(center_frame, text="Paragon Apartments", font=("Arial", 25, "bold"), bg=NAV_BG).pack()

    right_frame = _nav_frame(frame, side="right", padx=20, pady=20)
    create_button(right_frame, text=button_text, width=150, height=50,
                  bg=NAV_BTN, fg=BTN_FG, command=button_command,
                  current_window=parent).pack()

    return frame


def create_side_navbar(parent, button_text, user_info, button_command=None):
    sidebar_width = 190
    collapsed_width = 50
    collapsed = False 

    frame = tk.Frame(parent, bg=NAV_BG, width=sidebar_width)
    frame.pack(side="left", fill="y")
    frame.pack_propagate(False)

    # 1. Logout Logic
    def logout_command():
        logout_page(frame, parent)

    # Info section
    info_frame = _nav_frame(frame, side="top", fill="x", pady=(20, 10))
    tk.Label(info_frame, text="👤", font=("Arial", 30), bg=NAV_BG).pack(side="top", pady=(0, 5))
    tk.Label(info_frame, text=f"{user_info[1]} {user_info[2]} ({user_info[3]})", 
             font=("Arial", 12, "bold"), bg=NAV_BG).pack(side="top")
    tk.Label(info_frame, text=f"{user_info[4]}", font=("Arial", 10), bg=NAV_BG).pack(side="top")

    # 2. Middle Container (Spreads the middle buttons)
    nav_container = tk.Frame(frame, bg=NAV_BG)
    
    nav_buttons = []
    for i, text in enumerate(button_text):
        if text.strip().lower() == "logout": continue
        cmd = button_command[i] if isinstance(button_command, list) else button_command
        btn = create_button(nav_container, text=text, width=sidebar_width, height=50,
                           bg=NAV_BG, fg="black", command=cmd, current_window=parent)
        nav_buttons.append(btn)

    # 3. Footer Buttons
    # Added command=logout_command here to make it work
    logout_btn = create_button(frame, text="Logout", width=sidebar_width, height=40,
                               bg="#E53935", fg="white", command=logout_command, 
                               current_window=parent)
    
    toggle_btn = create_button(frame, text="←", width=sidebar_width, height=40,
                               bg=NAV_BTN, fg=BTN_FG)

    def _apply_sidebar_state():
        nonlocal collapsed
        current_w = collapsed_width if collapsed else sidebar_width
        frame.configure(width=current_w)

        # Clear layout to re-draw
        info_frame.pack_forget()
        nav_container.pack_forget()
        for btn in nav_buttons: btn.pack_forget()
        logout_btn.pack_forget()
        toggle_btn.pack_forget()

        # Update widths and CENTER text/rect for all buttons
        for b in nav_buttons + [logout_btn, toggle_btn]:
            h = 50 if b in nav_buttons else 40
            b.config(width=current_w)
            b.coords("rect", 0, 0, current_w, h)
            b.coords("text", current_w // 2, h // 2)

        # --- PACKING LOGIC ---
        toggle_btn.pack(side="bottom", fill="x")
        logout_btn.pack(side="bottom", fill="x")

        if not collapsed:
            info_frame.pack(side="top", fill="x", pady=(20, 10))
            nav_container.pack(side="top", fill="both", expand=True)
            for btn in nav_buttons:
                btn.pack(side="top", fill="x", expand=True)
            
            logout_btn.itemconfig("text", text="Logout")
            toggle_btn.itemconfig("text", text="←")
        else:
            logout_btn.itemconfig("text", text="")
            toggle_btn.itemconfig("text", text="→")

    toggle_btn.tag_bind("rect", "<Button-1>", lambda e: do_toggle())
    toggle_btn.tag_bind("text", "<Button-1>", lambda e: do_toggle())

    def do_toggle():
        nonlocal collapsed
        collapsed = not collapsed
        _apply_sidebar_state()

    _apply_sidebar_state()
    return frame
    

# --- Rest of the helper functions unchanged ---

def styled_label(parent, text, font=FONT_LABEL, fg="#333333"):
    return tk.Label(parent, text=text, font=font, bg=BG, fg=fg)

def styled_entry(parent):
    frame = tk.Frame(parent, bg="#E0E0E0", bd=0)
    inner = tk.Frame(frame, bg=BG, padx=2, pady=2)
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    e = tk.Entry(inner, font=FONT_ENTRY, bg=BG, relief="flat",
                 fg="#222", insertbackground="#222", width=ENTRY_W)
    e.pack(fill="both", ipady=8)
    return frame, e

def styled_dropdown(parent, values):
    style = ttk.Style()
    style.configure("Flat.TCombobox", fieldbackground=BG, background=BG,
                    foreground="#222", arrowsize=14, padding=6)
    var = tk.StringVar()
    cb = ttk.Combobox(parent, textvariable=var, values=values,
                      state="readonly", width=ENTRY_W, font=FONT_ENTRY,
                      style="Flat.TCombobox")
    return cb, var

def _form_label(container, label_text):
    styled_label(container, label_text, fg="#555").pack(anchor="w", pady=(10, 2))

def create_entry(parent, row, label_text, label_size, show=None):
    system_font = "Helvetica Neue" if platform.system() == "Darwin" else "Arial"
    tk.Label(parent, text=label_text, font=(system_font, label_size), bg=BG).grid(
        row=row, column=0, padx=25, pady=40, sticky="e")
    entry = tk.Entry(parent, show=show, font=(system_font, label_size),
                     bg=BG, bd=1, relief="groove",
                     highlightthickness=1, highlightbackground="#cccccc",
                     highlightcolor=NAV_BTN)
    entry.grid(row=row, column=1, padx=25, pady=20, sticky="w", ipady=5)
    return entry

def form_field(container, label_text, row_tracker=None):
    _form_label(container, label_text)
    border, entry = styled_entry(container)
    border.pack(fill="x")
    return entry


def _parse_date_or_default(value, fallback=None):
    if isinstance(value, date):
        return value

    raw_value = "" if value is None else str(value).strip()
    if raw_value:
        try:
            return datetime.strptime(raw_value, "%Y-%m-%d").date()
        except ValueError:
            pass

    return fallback or date.today()


def _resolve_date_constraint(value, fallback=None):
    if callable(value):
        try:
            value = value()
        except Exception:
            value = fallback

    return _parse_date_or_default(value, fallback=fallback)


class CalendarPopup(tk.Toplevel):
    def __init__(self, parent, initial_date, on_select, minimum_date=None):
        super().__init__(parent)
        self.on_select = on_select
        self.minimum_date = _resolve_date_constraint(minimum_date, fallback=date.today())
        self.selected_date = _parse_date_or_default(initial_date, fallback=self.minimum_date)
        if self.selected_date < self.minimum_date:
            self.selected_date = self.minimum_date
        self.displayed_year = self.selected_date.year
        self.displayed_month = self.selected_date.month

        self.title("Select Date")
        self.configure(bg="white")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self.picker_mode = False
        self.prev_button = None
        self.next_button = None
        self.header_label = None
        self.weekday_row = None
        self.days_frame = None

        self._build()
        self._position_near(parent)
        self.bind("<Escape>", lambda _event: self.destroy())
        self.focus_force()

    def _build(self):
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", padx=10, pady=(10, 6))

        self.prev_button = create_button(
            header,
            text="<",
            width=44,
            height=32,
            bg="#F2F4F7",
            fg="#222222",
            command=lambda: self._navigate(-1),
            auto_pack=False,
        )
        self.prev_button.pack(side="left")

        header_box = tk.Frame(
            header,
            bg="white",
            bd=1,
            relief="solid",
            cursor="hand2",
            padx=10,
            pady=4,
        )
        header_box.pack(side="left", expand=True, padx=8)

        self.header_label = tk.Label(
            header_box,
            text="",
            bg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2",
        )
        self.header_label.pack()
        header_box.bind("<Button-1>", lambda _event: self._toggle_picker_mode())
        self.header_label.bind("<Button-1>", lambda _event: self._toggle_picker_mode())

        self.next_button = create_button(
            header,
            text=">",
            width=44,
            height=32,
            bg="#F2F4F7",
            fg="#222222",
            command=lambda: self._navigate(1),
            auto_pack=False,
        )
        self.next_button.pack(side="right")

        self.weekday_row = tk.Frame(self, bg="white")
        self.weekday_row.pack(fill="x", padx=10)
        for weekday in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            tk.Label(
                self.weekday_row,
                text=weekday,
                width=4,
                bg="white",
                fg="#555555",
                font=("Arial", 9, "bold"),
            ).pack(side="left")

        self.days_frame = tk.Frame(self, bg="white")
        self.days_frame.pack(fill="both", padx=10, pady=(6, 10))
        self._render_current_view()

    def _position_near(self, parent):
        self.update_idletasks()
        x = parent.winfo_rootx()
        below_y = parent.winfo_rooty() + parent.winfo_height() + 4
        popup_height = self.winfo_reqheight()
        screen_height = self.winfo_screenheight()

        if below_y + popup_height > screen_height:
            y = max(0, parent.winfo_rooty() - popup_height - 4)
        else:
            y = below_y

        self.geometry(f"+{x}+{y}")

    def _navigate(self, delta):
        if self.picker_mode:
            next_year = self.displayed_year + delta
            if next_year < self.minimum_date.year:
                return
            self.displayed_year = next_year
            self._render_current_view()
            return

        self._change_month(delta)

    def _change_month(self, delta):
        month_index = self.displayed_month - 1 + delta
        self.displayed_year += month_index // 12
        self.displayed_month = month_index % 12 + 1
        self._render_current_view()

    def _toggle_picker_mode(self):
        self.picker_mode = not self.picker_mode
        self._render_current_view()

    def _render_current_view(self):
        if self.picker_mode:
            self._render_month_picker()
        else:
            self._render_days()

    def _sync_navigation_state(self):
        if self.picker_mode:
            self.prev_button.config(state="disabled" if self.displayed_year <= self.minimum_date.year else "normal")
        else:
            current_index = (self.displayed_year, self.displayed_month)
            minimum_index = (self.minimum_date.year, self.minimum_date.month)
            self.prev_button.config(state="disabled" if current_index <= minimum_index else "normal")

        self.next_button.config(state="normal")

    def _render_month_picker(self):
        self.header_label.config(text=str(self.displayed_year))
        self._sync_navigation_state()

        if self.weekday_row.winfo_manager():
            self.weekday_row.pack_forget()

        for widget in self.days_frame.winfo_children():
            widget.destroy()

        for month_index in range(1, 13):
            row_index = (month_index - 1) // 3
            column_index = (month_index - 1) % 3
            month_name = calendar.month_abbr[month_index]
            is_disabled = (
                self.displayed_year < self.minimum_date.year
                or (self.displayed_year == self.minimum_date.year and month_index < self.minimum_date.month)
            )
            is_selected = (
                self.displayed_year == self.selected_date.year
                and month_index == self.selected_date.month
            )

            button = create_button(
                self.days_frame,
                text=month_name,
                width=78,
                height=34,
                bg="#3B86FF" if is_selected else ("#E2E2E2" if is_disabled else "white"),
                fg="#9A9A9A" if is_disabled else ("white" if is_selected else "black"),
                state="disabled" if is_disabled else "normal",
                command=lambda chosen_month=month_index: self._select_month(chosen_month),
                auto_pack=False,
            )
            button.grid(row=row_index, column=column_index, padx=4, pady=4, sticky="nsew")

        for column_index in range(3):
            self.days_frame.grid_columnconfigure(column_index, weight=1)

    def _render_days(self):
        self.header_label.config(
            text=f"{calendar.month_name[self.displayed_month]} {self.displayed_year}"
        )
        self._sync_navigation_state()

        if not self.weekday_row.winfo_manager():
            self.weekday_row.pack(fill="x", padx=10, before=self.days_frame)

        for widget in self.days_frame.winfo_children():
            widget.destroy()

        month_matrix = calendar.Calendar(firstweekday=0).monthdayscalendar(
            self.displayed_year,
            self.displayed_month,
        )

        for row_index, week in enumerate(month_matrix):
            week_frame = tk.Frame(self.days_frame, bg="white")
            week_frame.grid(row=row_index, column=0, sticky="w")
            for day_number in week:
                if day_number == 0:
                    tk.Label(week_frame, text="", width=4, bg="white").pack(side="left")
                    continue

                is_selected = (
                    self.selected_date.year == self.displayed_year
                    and self.selected_date.month == self.displayed_month
                    and self.selected_date.day == day_number
                )
                candidate_date = date(self.displayed_year, self.displayed_month, day_number)
                is_disabled = candidate_date < self.minimum_date

                button = create_button(
                    week_frame,
                    text=str(day_number),
                    width=34,
                    height=30,
                    bg="#3B86FF" if is_selected else ("#E2E2E2" if is_disabled else "white"),
                    fg="#9A9A9A" if is_disabled else ("white" if is_selected else "black"),
                    state="disabled" if is_disabled else "normal",
                    command=lambda chosen_day=day_number: self._select_day(chosen_day),
                    auto_pack=False,
                )
                button.pack(side="left", padx=1, pady=1)

    def _select_month(self, month_number):
        self.displayed_month = month_number
        self.picker_mode = False
        self._render_current_view()

    def _select_day(self, day_number):
        chosen_date = date(self.displayed_year, self.displayed_month, day_number)
        self.on_select(chosen_date.isoformat())
        self.destroy()


def create_date_input(parent, initial_value="", minimum_date=None):
    frame = tk.Frame(parent, bg=parent.cget("bg"))
    border = tk.Frame(frame, bg="#E0E0E0", bd=0)
    border.pack(side="left", fill="x", expand=True)

    inner = tk.Frame(border, bg=BG, padx=2, pady=2)
    inner.pack(fill="both", expand=True, padx=1, pady=1)

    entry = tk.Entry(
        inner,
        font=("Arial", 10),
        bg=BG,
        relief="flat",
        fg="#222",
        insertbackground="#222",
        width=ENTRY_W,
    )
    entry.pack(fill="both", ipady=3)

    if initial_value:
        entry.insert(0, initial_value)

    def open_calendar():
        initial_date = _parse_date_or_default(entry.get())
        CalendarPopup(
            frame,
            initial_date,
            lambda value: _set_entry_value(entry, value),
            minimum_date=minimum_date,
        )

    button = create_button(
        frame,
        text="...",
        width=42,
        height=28,
        bg="#3B86FF",
        fg="white",
        command=open_calendar,
        auto_pack=False,
    )
    button.pack(side="left", padx=(6, 0), ipady=1)

    return frame, entry


def _set_entry_value(entry, value):
    entry.delete(0, tk.END)
    entry.insert(0, value)


def show_lease_removal_confirmation(parent, tenant_name, apartment_display, lease_end, vacate_by, penalty):
    """Show a custom modal confirmation with red warning text for lease removal."""
    details = [
        f"Tenant: {tenant_name}",
        f"Apartment: {apartment_display}",
        f"Lease End: {lease_end}",
        f"Vacate By: {vacate_by}",
        f"Penalty (5%): £{penalty:,.2f}",
    ]
    warning_lines = [
        "Warning: Deleting this lease applies a penalty equal to 5% of",
        "the monthly payment.",
        "Notice: A minimum 1 month notice applies.",
        "By agreeing, you accept the 5% early termination penalty.",
    ]

    owner = None
    if parent is not None and hasattr(parent, "winfo_toplevel"):
        try:
            owner = parent.winfo_toplevel()
        except Exception:
            owner = None

    if owner is None:
        message = "\n".join(details + [""] + warning_lines)
        return messagebox.askyesno("Confirm Removal", message)

    dialog = tk.Toplevel(owner)
    dialog.title("Confirm Removal")
    dialog.configure(bg="white")
    dialog.resizable(False, False)
    if owner is not None:
        dialog.transient(owner)
    dialog.grab_set()

    result = {"confirmed": False}

    container = tk.Frame(dialog, bg="white", padx=18, pady=16)
    container.pack(fill="both", expand=True)

    for line in details:
        tk.Label(
            container,
            text=line,
            bg="white",
            fg="#222222",
            font=("Arial", 11, "bold"),
            justify="center",
        ).pack(anchor="center", pady=1)

    tk.Frame(container, bg="white", height=16).pack()

    for line in warning_lines:
        tk.Label(
            container,
            text=line,
            bg="white",
            fg="#C62828",
            font=("Arial", 10, "bold"),
            justify="center",
        ).pack(anchor="center", pady=1)

    button_row = tk.Frame(container, bg="white")
    button_row.pack(fill="x", pady=(18, 0))

    def _close(confirmed):
        result["confirmed"] = confirmed
        dialog.destroy()

    create_button(
        button_row,
        text="No",
        width=120,
        height=42,
        bg="#E8ECEF",
        fg="#222222",
        command=lambda: _close(False),
        auto_pack=False,
    ).pack(side="left", padx=(0, 8))

    create_button(
        button_row,
        text="Yes",
        width=120,
        height=42,
        bg="#3B86FF",
        fg="white",
        command=lambda: _close(True),
        auto_pack=False,
    ).pack(side="right", padx=(8, 0))

    dialog.bind("<Escape>", lambda _event: _close(False))
    dialog.protocol("WM_DELETE_WINDOW", lambda: _close(False))

    dialog.update_idletasks()
    if owner is not None:
        owner_x = owner.winfo_rootx()
        owner_y = owner.winfo_rooty()
        owner_w = owner.winfo_width()
        owner_h = owner.winfo_height()
        dialog_w = dialog.winfo_reqwidth()
        dialog_h = dialog.winfo_reqheight()
        pos_x = owner_x + max((owner_w - dialog_w) // 2, 0)
        pos_y = owner_y + max((owner_h - dialog_h) // 2, 0)
        dialog.geometry(f"+{pos_x}+{pos_y}")

    dialog.wait_window()
    return result["confirmed"]

def form_dropdown(container, label_text, values):
    _form_label(container, label_text)
    cb, var = styled_dropdown(container, values)
    cb.pack(fill="x", ipady=4)
    return cb

def card(parent):
    shadow = tk.Frame(parent, bg="#D0D0D0")
    shadow.place(relx=0.5, rely=0.5, anchor="center")
    inner = tk.Frame(shadow, bg=BG, padx=32, pady=28)
    inner.pack(padx=2, pady=2)
    return inner

def logout_page(current_frame, parent_widget):
    try:
        root = parent_widget.winfo_toplevel()
        if root: root.destroy()
        from main.index import main_window
        main_window()
    except Exception as e:
        import tkinter.messagebox as messagebox
        messagebox.showerror("Logout Error", f"Could not return to index page: {e}")

def create_logout_button(parent_frame, target_frame, parent_widget, anchor="ne", padx=10, pady=0):
    from main.helpers import logout_page
    btn = create_button(
        parent_frame,
        text="➜]",
        width=35,
        height=35,
        bg="#FF3B3B",
        fg="white",
        command=lambda: logout_page(target_frame, parent_widget.winfo_toplevel()),
    )
    btn.pack(anchor=anchor, padx=padx, pady=pady)
    return btn

def create_scrollable_treeview(parent, columns, headings, widths, anchors, height=9):
    table_wrap = tk.Frame(parent, bg="white", bd=2, relief="groove")
    table_wrap.pack(fill="both", expand=True, pady=(0, 12))
    tree = ttk.Treeview(table_wrap, columns=columns, show="headings", height=height)
    for col, heading, width, anchor in zip(columns, headings, widths, anchors):
        tree.heading(col, text=heading)
        tree.column(col, width=width, anchor=anchor)
    y_scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=y_scroll.set)
    tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
    y_scroll.pack(side="right", fill="y", pady=8, padx=(0, 8))
    return table_wrap, tree

def _get_treeview_empty_state_label(tree):
    label = getattr(tree, "_empty_state_label", None)

    try:
        if label is not None and label.winfo_exists():
            return label
    except tk.TclError:
        pass

    parent = getattr(tree, "master", None)
    if parent is None:
        return None

    parent_bg = parent.cget("bg") if hasattr(parent, "cget") else "white"
    label = tk.Label(
        parent,
        text="No records found.",
        bg=parent_bg,
        fg="#888888",
        font=("Arial", 11, "italic"),
        padx=12,
        pady=8,
    )
    tree._empty_state_label = label
    return label

def set_treeview_empty_state(tree, has_records, message="No records found."):
    if tree is None:
        return

    label = _get_treeview_empty_state_label(tree)
    if label is None:
        return

    if has_records:
        label.place_forget()
        return

    label.config(text=message)
    label.place(relx=0.5, rely=0.5, anchor="center")
    label.lift()

def reset_combobox(combobox, names):
    combobox.set(names[0] if names else "")

def show_placeholder(parent, text=""):
    for widget in parent.winfo_children():
        widget.destroy()
    tk.Label(
        parent,
        text=text,
        bg="white",
        fg="#888888",
        font=("Arial", 10, "italic"),
        pady=16,
    ).pack(expand=True)