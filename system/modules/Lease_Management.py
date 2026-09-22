# LEASE MANAGEMENT MODULE
# Handles lease creation and removal with early termination penalties
# ============================================================================
# Leyla Ahmed (24060594)  

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import date, timedelta

from main.helpers import (
    create_button, clear_frame,
    styled_label, form_field, form_dropdown, card, create_date_input,
    BG, ACCENT, FONT_TITLE, show_lease_removal_confirmation,
)

from database.lease_service import (
    fetch_leases, fetch_tenants,
    create_lease, build_tenant_map,
    update_lease_early_termination,
)
from database.property_service import build_apartment_map, fetch_available_apartments

from validations import validate_lease_selection, validate_lease_details
from validations import minimum_lease_end_date


# ============================================================================
# ADD LEASE STEPPER CLASS
# ============================================================================
class AddLeaseStepper:
    def __init__(self, parent, refresh_callback, city_id=None): 
        self.box_frame        = parent
        self.refresh_callback = refresh_callback
        self.city_id          = city_id 

        # FIX: Pass city_id to both fetch functions
        tenants    = fetch_tenants(city_id=self.city_id)
        apartments = fetch_available_apartments(city_id=self.city_id)

        # Rest of the code remains the same...
        self.tenant_map   = {t[1]: t[0] for t in tenants} # name: id
        self.tenant_names = list(self.tenant_map.keys())
        self.apt_map      = build_apartment_map(apartments)
        self.apt_displays = list(self.apt_map.keys())

        self.step_tenant()

    # ========================================================================
    # STEP 1: SELECT TENANT
    # ========================================================================

    def step_tenant(self):
        """First step: Select tenant"""
        clear_frame(self.box_frame)
        container = card(self.box_frame)

        # Step header
        styled_label(container, "Add Lease", font=FONT_TITLE, fg="#222").pack(pady=(0, 4))
        tk.Frame(container, bg=ACCENT, height=3, width=60).pack(pady=(0, 16))
        styled_label(container, "Step 1 of 3 — Select Tenant", fg="#888").pack(pady=(0, 8))

        # Check if tenants exist
        if not self.tenant_names:
            styled_label(container, "No tenants registered yet.", fg="#C62828").pack(pady=10)
            return

        # Tenant dropdown
        tenant_cb = form_dropdown(container, "Tenant", self.tenant_names)

        # Next button
        btn_frame = tk.Frame(container, bg=BG)
        btn_frame.pack(pady=(20, 0))
        create_button(
            btn_frame,
            text="Next →",
            width=150,
            height=50,
            bg="#3B86FF",
            fg="white",
            command=lambda: self.step_apartment(tenant_cb.get()),
            next_window_func=None,
            current_window=None,
        ).pack()

    # ========================================================================
    # STEP 2: SELECT APARTMENT
    # ========================================================================

    def step_apartment(self, tenant_name):
        """Second step: Select apartment"""
        clear_frame(self.box_frame)
        container = card(self.box_frame)

        # Step header
        styled_label(container, "Add Lease", font=FONT_TITLE, fg="#222").pack(pady=(0, 4))
        tk.Frame(container, bg=ACCENT, height=3, width=60).pack(pady=(0, 16))
        styled_label(container, "Step 2 of 3 — Select Apartment", fg="#888").pack(pady=(0, 8))
        styled_label(container, f"Tenant: {tenant_name}", fg="#555").pack(anchor="w")

        # Check if apartments available
        if not self.apt_displays:
            styled_label(container, "No vacant apartments available.", fg="#C62828").pack(pady=10)
            btn_frame = tk.Frame(container, bg=BG)
            btn_frame.pack(pady=(12, 0))
            create_button(
                btn_frame,
                text="← Back",
                width=150,
                height=50,
                bg="#3B86FF",
                fg="white",
                command=self.step_tenant,
                next_window_func=None,
                current_window=None,
            ).pack()
            return

        # Apartment dropdown
        apt_cb = form_dropdown(container, "Apartment (Vacant)", self.apt_displays)

        # Next button
        btn_frame = tk.Frame(container, bg=BG)
        btn_frame.pack(pady=(20, 0))
        create_button(
            btn_frame,
            text="Next →",
            width=150,
            height=50,
            bg="#3B86FF",
            fg="white",
            command=lambda: self.step_details(tenant_name, apt_cb.get()),
            next_window_func=None,
            current_window=None,
        ).pack()

    # ========================================================================
    # STEP 3: LEASE DETAILS
    # ========================================================================

    def step_details(self, tenant_name, apt_display):
        """Third step: Enter lease details"""
        clear_frame(self.box_frame)
        container = card(self.box_frame)

        # Step header
        styled_label(container, "Add Lease", font=FONT_TITLE, fg="#222").pack(pady=(0, 4))
        tk.Frame(container, bg=ACCENT, height=3, width=60).pack(pady=(0, 16))
        styled_label(container, "Step 3 of 3 — Lease Details", fg="#888").pack(pady=(0, 8))

        # Show selected tenant and apartment
        info = tk.Frame(container, bg="#F5F5F5", padx=12, pady=8)
        info.pack(fill="x", pady=(0, 12))
        styled_label(info, f"{tenant_name}  ·  {apt_display}", fg="#555").pack(anchor="w")

        # Date and rent fields
        styled_label(container, "Start Date (YYYY-MM-DD)", fg="#555").pack(anchor="w", pady=(10, 2))
        start_wrapper, start_entry = create_date_input(
            container,
            initial_value=date.today().isoformat(),
        )
        start_wrapper.pack(fill="x")

        styled_label(container, "End Date (YYYY-MM-DD)", fg="#555").pack(anchor="w", pady=(10, 2))
        end_wrapper, end_entry = create_date_input(
            container,
            initial_value=(date.today() + timedelta(days=365)).isoformat(),
            minimum_date=lambda: minimum_lease_end_date(
                _coerce_start_date(start_entry.get())
            ),
        )
        end_wrapper.pack(fill="x")

        rent_entry  = form_field(container, "Monthly Rent (£)",        [0])

        # Submit function
        def submit():
            try:
                # Validate selections
                validate_lease_selection(tenant_name, apt_display)
                
                # Validate details
                validate_lease_details(
                    start_entry.get(),
                    end_entry.get(),
                    rent_entry.get()
                )
                
                # Get IDs from lookup dictionaries
                tenant_id = self.tenant_map[tenant_name]
                apt_id    = self.apt_map[apt_display]
                
                # Create lease in database
                create_lease(
                    apartment_id=apt_id,
                    tenant_id=tenant_id,
                    start_date=start_entry.get(),
                    end_date=end_entry.get(),
                    agreed_rent=rent_entry.get()
                )
                
                # Show success message
                clear_frame(self.box_frame)
                styled_label(
                    self.box_frame,
                    "✓  Lease created successfully",
                    fg="#2E7D32",
                ).pack(expand=True)
                
                # Refresh and return to main view after 1.5 seconds
                self.box_frame.after(1500, self.refresh_callback)
                
            except Exception as err:
                messagebox.showerror("Error", str(err))

        # Action buttons
        btn_frame = tk.Frame(container, bg=BG)
        btn_frame.pack(pady=(20, 0))
        create_button(
            btn_frame,
            text="Create Lease",
            width=150,
            height=50,
            bg="#2E7D32",
            fg="white",
            command=submit,
            next_window_func=None,
            current_window=None,
        ).pack()


# ============================================================================
# REMOVE LEASE STEPPER CLASS
# ============================================================================
class RemoveLeaseStepper:
    def __init__(self, parent, refresh_callback):
        self.box_frame        = parent
        self.refresh_callback = refresh_callback
        self.leases           = fetch_leases()
        
        self.step_select()

    def step_select(self):
        """First step: Select a lease to remove"""
        clear_frame(self.box_frame)
        container = card(self.box_frame)

        # Header
        styled_label(container, "Remove Lease", font=FONT_TITLE, fg="#222").pack(pady=(0, 4))
        tk.Frame(container, bg=ACCENT, height=3, width=60).pack(pady=(0, 16))
        styled_label(container, "Step 1 of 2 — Select Lease", fg="#888").pack(pady=(0, 8))

        # Check if leases exist
        if not self.leases:
            styled_label(container, "No active leases found.", fg="#C62828").pack(pady=10)
            return

        # Display leases in dropdown format
        lease_options = []
        for lease in self.leases:
            l_id, tenant, apt, start, end, rent, city, status = lease
            lease_str = f"#{l_id} - {tenant} ({apt}) - {status}"
            lease_options.append(lease_str)

        lease_cb = form_dropdown(container, "Select Lease", lease_options)

        # Next button
        btn_frame = tk.Frame(container, bg=BG)
        btn_frame.pack(pady=(20, 0))
        create_button(
            btn_frame,
            text="Next →",
            width=150,
            height=50,
            bg="#3B86FF",
            fg="white",
            command=lambda: self.step_confirm(lease_cb.get()),
            next_window_func=None,
            current_window=None,
        ).pack()

    def step_confirm(self, lease_str):
        """Second step: Confirm removal with penalty calculation"""
        if not lease_str:
            messagebox.showerror("Error", "Please select a lease.")
            return

        # Extract lease ID from string (format: "#ID - ...")
        l_id = int(lease_str.split("#")[1].split(" ")[0])
        
        # Find the corresponding lease
        lease_data = next((l for l in self.leases if l[0] == l_id), None)
        if not lease_data:
            messagebox.showerror("Error", "Lease not found.")
            return

        _, tenant_name, apartment_display, _, end_date, rent, _, status = lease_data
        if status == "Terminated":
            messagebox.showinfo("Info", "This lease is already terminated.")
            return

        penalty = round(float(rent) * 0.05, 2)
        vacate_by = minimum_lease_end_date(date.today()).isoformat()

        if not show_lease_removal_confirmation(
            getattr(self, "box_frame", None),
            tenant_name,
            apartment_display,
            end_date,
            vacate_by,
            penalty,
        ):
            return

        try:
            update_lease_early_termination(l_id, penalty)
            messagebox.showinfo("Success", "Lease updated successfully.")
            self.refresh_callback()
        except Exception as e:
            messagebox.showerror("Error", f"Could not terminate lease: {e}")


def _coerce_start_date(raw_value):
    try:
        return date.fromisoformat(str(raw_value).strip())
    except Exception:
        return date.today()

def create_page(parent, user_info):
    """Factory function to create the appropriate lease page based on user role"""
    if not user_info or len(user_info) < 5:
        from main.lease_page import LeaseManagerPage
        return LeaseManagerPage(parent, user_info=None).frame
    
    role = user_info[4] 
    if role == "Tenant":
        frame = tk.Frame(parent, bg="#c9e4c4")
        box = tk.Frame(frame, bg="white", bd=2, relief="groove")
        box.pack(fill="both", expand=True, padx=40, pady=40)
        tk.Label(
            box,
            text="Tenant lease self-service has been removed.",
            bg="white",
            fg="#1f3b63",
            font=("Arial", 14, "bold"),
        ).pack(pady=(30, 8))
        tk.Label(
            box,
            text="Please contact staff for any lease questions or termination requests.",
            bg="white",
            fg="#4c5d73",
            font=("Arial", 11),
        ).pack(pady=(0, 30))
        return frame

    from main.lease_page import LeaseManagerPage
    page = LeaseManagerPage(parent, user_info=user_info)
    page.frame.on_show = page.on_show
    return page.frame
