# Erin Williams (23072947)  

import tkinter as tk
from tkinter import ttk, messagebox
from validations import validate_tenant_form


from main.helpers import create_button, set_treeview_empty_state

from database.tenant_service import (
    get_all_tenants,
    create_tenant,
    update_tenant,
    delete_tenant,
)


class TenantManagementPage:
    def __init__(self, parent, user_info=None):
        self.frame = tk.Frame(parent, bg="#c9e4c4")
        self.user_info = user_info
        self.user_role = user_info[4] if user_info and len(user_info) > 4 else None
        self.is_front_desk = self.user_role == "Front-desk Staff"
        self.user_id = user_info[0] if user_info else None
        self.assigned_city_id = user_info[5] if user_info and len(user_info) > 5 else None
        self.selected_tenant_id = None

        if self.user_role == "Tenant":
            self._build_removed_notice()
        else:
            self._build_layout()
            self._load_tenants()

    def on_show(self):
        if self.user_role != "Tenant":
            self._load_tenants()

    # ---------------------------------------------------
    def _build_removed_notice(self):
        wrap = tk.Frame(self.frame, bg="#c9e4c4")
        wrap.pack(fill="both", expand=True, padx=20, pady=20)

        box = tk.Frame(wrap, bg="white", bd=2, relief="groove")
        box.pack(fill="x", pady=(0, 12))

        tk.Label(
            box,
            text="Tenant self-service has been removed.",
            bg="white",
            fg="#1f3b63",
            font=("Arial", 16, "bold"),
        ).pack(anchor="w", padx=14, pady=(14, 6))

        tk.Label(
            box,
            text="Please contact staff for any profile, lease, complaint, or payment requests.",
            bg="white",
            fg="#4c5d73",
            font=("Arial", 11),
            wraplength=760,
            justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 14))

    # ---------------------------------------------------
    def _build_layout(self):
        top_btn_frame = tk.Frame(self.frame, bg="#c9e4c4")
        top_btn_frame.pack(side="top", fill="x", pady=(20, 8))

        btns_inner_frame = tk.Frame(top_btn_frame, bg="#c9e4c4")
        btns_inner_frame.pack(anchor="center")

        create_button(btns_inner_frame, "Add Tenant", 140, 45, "#3B86FF", "white", self.add_tenant).pack(side="left", padx=8)
        if self.user_role != "Front-desk Staff":
            create_button(btns_inner_frame, "Update Tenant", 140, 45, "#3B86FF", "white", self.update_tenant).pack(side="left", padx=8)
            create_button(btns_inner_frame, "Delete Tenant", 140, 45, "#3B86FF", "white", self.delete_tenant).pack(side="left", padx=8)

        content_frame = tk.Frame(self.frame, bg="#c9e4c4")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(6, 20))

        table_wrap = tk.Frame(content_frame, bg="white", bd=2, relief="groove")
        table_wrap.pack(fill="both", expand=True, pady=(0, 12))

        columns = (
            "tenant_id", "first_name", "surname", "email", "telephone",
            "reference_name", "reference_email", "ni_number",
            "lease_period", "apartment_type", "occupation"
        )

        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings", height=9)

        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())

        self.tree.column("tenant_id", width=55, anchor="center")
        self.tree.column("first_name", width=120)
        self.tree.column("surname", width=120)
        self.tree.column("email", width=180)
        self.tree.column("telephone", width=120)
        self.tree.column("reference_name", width=150)
        self.tree.column("reference_email", width=180)
        self.tree.column("ni_number", width=150)
        self.tree.column("lease_period", width=120)
        self.tree.column("apartment_type", width=140)
        self.tree.column("occupation", width=140)

        y_scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=y_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        y_scroll.pack(side="right", fill="y", pady=8, padx=(0, 8))

        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

        form = tk.Frame(content_frame, bg="white", bd=2, relief="groove")
        form.pack(fill="x", padx=0)

        self.first_name_entry = self._form_field(form, "First Name", 0, 0)
        self.surname_entry = self._form_field(form, "Surname", 0, 2)
        self.email_entry = self._form_field(form, "Email", 0, 4)

        self.telephone_entry = self._form_field(form, "Telephone", 1, 0)
        self.reference_name_entry = self._form_field(form, "Reference Name", 1, 2)
        self.reference_email_entry = self._form_field(form, "Reference Email", 1, 4)

        self.ni_entry = self._form_field(form, "National Insurance Number", 2, 0)
        self.lease_period_entry = self._form_field(form, "Lease Period", 2, 2)
        self.apartment_type_entry = self._form_field(form, "Apartment Type", 2, 4)

        # Derived fields from Lease/Apartments are display-only in tenant management.
        self.lease_period_entry.config(state="readonly")
        self.apartment_type_entry.config(state="readonly")

        self.occupation_entry = self._form_field(form, "Occupation", 3, 0)

        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(3, weight=1)
        form.grid_columnconfigure(5, weight=1)

    # ---------------------------------------------------
    def _form_field(self, parent, label, row, col):
        tk.Label(parent, text=label, bg="white", font=("Arial", 11, "bold")).grid(
            row=row, column=col, padx=(16, 6), pady=8, sticky="w"
        )
        entry = tk.Entry(parent, width=30)
        entry.grid(row=row, column=col + 1, padx=(0, 16), pady=8, sticky="we")
        return entry

    # ---------------------------------------------------
    def _load_tenants(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        tenants = self._get_scoped_tenants()

        for tenant in tenants:
            self.tree.insert("", "end", values=tenant)

        set_treeview_empty_state(self.tree, bool(tenants))

    def _get_scoped_tenants(self):
        city_id = self.assigned_city_id if self.user_role in ["Administrators", "Front-desk Staff"] else None
        return get_all_tenants(city_id=city_id)

    # ---------------------------------------------------
    def _on_row_select(self, _event=None):
        if self.is_front_desk:
            # Front-desk can view records in table, but form remains add-only.
            return

        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        self.selected_tenant_id = int(values[0])

        entries = [
            self.first_name_entry, self.surname_entry, self.email_entry,
            self.telephone_entry, self.reference_name_entry, self.reference_email_entry,
            self.ni_entry, self.lease_period_entry, self.apartment_type_entry,
            self.occupation_entry
        ]

        for entry, value in zip(entries, values[1:]):
            # Temporarily unlock readonly entries so selected row values can be displayed.
            if str(entry.cget("state")) == "readonly":
                entry.config(state="normal")
                entry.delete(0, tk.END)
                entry.insert(0, value)
                entry.config(state="readonly")
            else:
                entry.delete(0, tk.END)
                entry.insert(0, value)

    def _clear_form(self):
        entries = [
            self.first_name_entry, self.surname_entry, self.email_entry,
            self.telephone_entry, self.reference_name_entry, self.reference_email_entry,
            self.ni_entry, self.lease_period_entry, self.apartment_type_entry,
            self.occupation_entry,
        ]

        for entry in entries:
            if str(entry.cget("state")) == "readonly":
                entry.config(state="normal")
                entry.delete(0, tk.END)
                entry.config(state="readonly")
            else:
                entry.delete(0, tk.END)

        self.selected_tenant_id = None

    # ---------------------------------------------------
    def add_tenant(self):
        try:
            data = self._collect_form_data()
            validate_tenant_form(data)
            create_tenant(*data, city_id=self.assigned_city_id)
            self._load_tenants()
            self._clear_form()
            messagebox.showinfo("Success", "Tenant added successfully.", parent=self.frame)
        except Exception as error:
            messagebox.showerror("Error", str(error))

    # ---------------------------------------------------
    def update_tenant(self):
        if self.user_role == "Front-desk Staff":
            messagebox.showerror("Permission Denied", "Front-desk Staff cannot update tenant records.")
            return

        if self.selected_tenant_id is None:
            messagebox.showerror("Selection Error", "Please select a tenant first.")
            return

        try:
            data = self._collect_form_data()
            validate_tenant_form(data)
            update_tenant(self.selected_tenant_id, *data)
            self._load_tenants()
            messagebox.showinfo("Success", "Tenant updated successfully.")
        except Exception as error:
            messagebox.showerror("Error", str(error))

    # ---------------------------------------------------
    def delete_tenant(self):
        if self.user_role == "Front-desk Staff":
            messagebox.showerror("Permission Denied", "Front-desk Staff cannot delete tenant records.")
            return

        if self.selected_tenant_id is None:
            messagebox.showerror("Selection Error", "Please select a tenant first.")
            return

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this tenant?"):
            return

        try:
            delete_tenant(self.selected_tenant_id)
            self.selected_tenant_id = None
            self._load_tenants()
            messagebox.showinfo("Success", "Tenant deleted successfully.")
        except Exception as error:
            messagebox.showerror("Error", str(error))

    # ---------------------------------------------------
    def _collect_form_data(self):
        reference_name = self.reference_name_entry.get().strip()
        reference_email = self.reference_email_entry.get().strip()

        # Treat placeholders as empty optional values.
        if reference_name.lower() in {"none", "-"}:
            reference_name = ""
        if reference_email.lower() in {"none", "-"}:
            reference_email = ""

        return (
            self.first_name_entry.get().strip(),
            self.surname_entry.get().strip(),
            self.email_entry.get().strip(),
            self.telephone_entry.get().strip(),
            reference_name,
            reference_email,
            self.ni_entry.get().strip(),
            self.lease_period_entry.get().strip(),
            self.apartment_type_entry.get().strip(),
            self.occupation_entry.get().strip(),
        )

def create_page(parent, user_info=None):
    page = TenantManagementPage(parent, user_info=user_info)
    page.frame.on_show = page.on_show
    return page.frame
