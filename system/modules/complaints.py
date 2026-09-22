# Erin Williams (23072947)  

import tkinter as tk
from tkinter import ttk, messagebox
from database.tenant_service import get_all_tenants, get_all_complaints_with_tenant, add_complaint
from main.helpers import create_button, set_treeview_empty_state

def create_page(parent, user_info=None):
    frame = tk.Frame(parent, bg='#c9e4c4')
    role = user_info[4] if user_info and len(user_info) > 4 else None

    if role == "Front-desk Staff":
        assigned_city_id = user_info[5] if user_info and len(user_info) > 5 else None

        top_btn_frame = tk.Frame(frame, bg='#c9e4c4')
        top_btn_frame.pack(side="top", fill="x", pady=(30, 10))

        btns_inner_frame = tk.Frame(top_btn_frame, bg='#c9e4c4')
        btns_inner_frame.pack(anchor="center")

        form_box = tk.Frame(btns_inner_frame, bg="#c9e4c4")
        form_box.pack(anchor="center")

        tk.Label(form_box, text="Tenant", bg="#c9e4c4", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=6, pady=4, sticky="w")

        tenant_map = {}
        tenant_var = tk.StringVar(value="")
        tenant_cb = ttk.Combobox(form_box, textvariable=tenant_var, values=[], state="readonly", width=30)
        tenant_cb.grid(row=0, column=1, padx=6, pady=4)

        def refresh_tenant_dropdown():
            current_selection = tenant_var.get().strip()
            tenants = get_all_tenants(city_id=assigned_city_id)
            tenant_options = [f"{row[0]} - {row[1]} {row[2]}" for row in tenants]

            tenant_map.clear()
            tenant_map.update({f"{row[0]} - {row[1]} {row[2]}": int(row[0]) for row in tenants})

            tenant_cb["values"] = tenant_options
            if current_selection in tenant_map:
                tenant_var.set(current_selection)
            elif tenant_options:
                tenant_var.set(tenant_options[0])
            else:
                tenant_var.set("")

        tk.Label(form_box, text="Complaint", bg="#c9e4c4", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=6, pady=4, sticky="w")
        description_entry = tk.Entry(form_box, width=42)
        description_entry.grid(row=0, column=3, padx=6, pady=4)

        box_frame = tk.Frame(frame, bg="white", bd=2, relief="groove")
        box_frame.pack(fill="both", expand=True, padx=40, pady=(10, 40))

        columns = ("id", "tenant_id", "name", "description", "date")
        tree = ttk.Treeview(box_frame, columns=columns, show="headings", height=16)

        tree.heading("id", text="Complaint ID")
        tree.heading("tenant_id", text="Tenant ID")
        tree.heading("name", text="Tenant Name")
        tree.heading("description", text="Complaint Description")
        tree.heading("date", text="Date Submitted")

        tree.column("id", width=100, anchor="center")
        tree.column("tenant_id", width=100, anchor="center")
        tree.column("name", width=180, anchor="w")
        tree.column("description", width=500, anchor="w")
        tree.column("date", width=150, anchor="center")

        y_scroll = ttk.Scrollbar(box_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=y_scroll.set)

        tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        y_scroll.pack(side="right", fill="y", pady=8, padx=(0, 8))

        def load_staff_complaints():
            tree.delete(*tree.get_children())
            rows = get_all_complaints_with_tenant(city_id=assigned_city_id)
            for complaint_id, tenant_id, first, surname, description, date_submitted in rows:
                tree.insert("", "end", values=(complaint_id, tenant_id, f"{first} {surname}", description, date_submitted))

            set_treeview_empty_state(tree, bool(rows))

        def submit_staff_complaint():
            tenant_key = tenant_var.get().strip()
            description = description_entry.get().strip()

            if tenant_key not in tenant_map:
                messagebox.showerror("Validation Error", "Please select a valid tenant.")
                return
            if len(description) < 3:
                messagebox.showerror("Validation Error", "Complaint text must be at least 3 characters.")
                return

            add_complaint(tenant_map[tenant_key], description)
            description_entry.delete(0, tk.END)
            load_staff_complaints()
            messagebox.showinfo("Success", "Complaint submitted.")

        create_button(
            form_box,
            text="Submit Complaint",
            width=150,
            height=36,
            bg="#3B86FF",
            fg="white",
            command=submit_staff_complaint,
            auto_pack=False,
        ).grid(row=0, column=4, padx=6, pady=4)

        def on_show_staff_complaints():
            refresh_tenant_dropdown()
            load_staff_complaints()

        on_show_staff_complaints()
        frame.on_show = on_show_staff_complaints
        return frame

    box_frame = tk.Frame(frame, bg="white", bd=2, relief="groove")
    box_frame.pack(fill="both", expand=True, padx=40, pady=(20, 40))
    tk.Label(
        box_frame,
        text="Complaints are handled by Front-desk Staff.",
        bg="white",
        font=("Arial", 14, "bold"),
        fg="#1f3b63",
    ).pack(expand=True)
    return frame