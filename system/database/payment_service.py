# Momchil Georgiev (24033989)
from .db_utils import execute_query, get_user_city_id, get_user_role
from database.lease_service import sync_lease_payments_up_to_horizon
from database.tenant_service import ensure_tenant_contact_schema


def _resolve_finance_scope_city_id(user_info=None, city_id=None):
    """Resolve the city scope for finance-manager payment access."""
    if city_id is not None:
        return city_id

    if get_user_role(user_info) == "Finance Manager":
        return get_user_city_id(user_info)

    return None


def update_late_status():
    """Updates the 'is_late' column. Late if past due date and unpaid/underpaid."""
    # Keep payment schedules rolling monthly without generating far-future rows.
    sync_lease_payments_up_to_horizon(months_ahead=1)

    execute_query(
        """
        UPDATE Payment
        SET is_late = CASE
            WHEN payment_date IS NOT NULL
                 AND DATE(payment_date) > DATE(due_date)
            THEN 'Yes'
            WHEN DATE(due_date) < DATE('now')
                 AND (
                     payment_date IS NULL
                     OR amount < (
                         SELECT Agreed_rent
                         FROM Lease
                         WHERE Lease.lease_id = Payment.lease_id
                     )
                 )
            THEN 'Yes'
            ELSE 'No'
        END
        """,
        (),
        'none'
    )


def get_tenant_payments(user_id):
    """
    Tenant view:
    - one row per lease
    - only leases from the tenant's own city
    """
    update_late_status()
    
    rows = execute_query(
        """
        SELECT
            l.lease_id,
            b.street || ' (' || b.postcode || ')' AS apartment,
            COALESCE(MAX(p.due_date), DATE('now')) AS due_date,
            COALESCE(SUM(CASE WHEN p.payment_date IS NOT NULL THEN p.amount ELSE 0 END), 0) AS paid_amount,
            l.Agreed_rent,
            CASE
                WHEN COALESCE(SUM(CASE WHEN p.payment_date IS NOT NULL THEN p.amount ELSE 0 END), 0) >= l.Agreed_rent
                THEN 'Paid'
                ELSE 'Unpaid'
            END AS status,
            MAX(COALESCE(p.is_late, 'No')) AS is_late,
            COALESCE(MAX(p.payment_id), 0) AS payment_id
        FROM Lease l
        JOIN Tenant t ON l.tenant_id = t.tenant_id
        JOIN User u ON t.user_id = u.user_id
        JOIN Apartments a ON l.apartment_id = a.apartment_id
        JOIN Buildings b ON a.building_id = b.building_id
        LEFT JOIN Payment p ON p.lease_id = l.lease_id
        WHERE t.user_id = ?
          AND b.city_id = u.city_id
        GROUP BY l.lease_id, apartment, l.Agreed_rent
        ORDER BY DATE(due_date) DESC, l.lease_id DESC
        """,
        (user_id,)
    )

    out = []
    for lease_id, apartment, due_date, paid_amount, agreed_rent, status, is_late, payment_id in rows:
        payment_date = "-" if status == "Unpaid" else "Paid / Partial"
        out.append(
            (
                apartment,
                due_date,
                payment_date,
                round(float(paid_amount or 0), 2),
                round(float(agreed_rent or 0), 2),
                status,
                is_late or "No",
                int(payment_id or 0),
            )
        )
    return out


def get_all_payments(user_info=None, city_id=None):
    """Retrieves all payment records for Finance Manager."""
    update_late_status()

    scope_city_id = _resolve_finance_scope_city_id(user_info=user_info, city_id=city_id)
    params = []
    where_clause = ""

    if scope_city_id is not None:
        where_clause = "WHERE b.city_id = ?"
        params.append(scope_city_id)

    return execute_query(
        f"""
        SELECT u.first_name || ' ' || u.surname as tenant_name,
               b.street || ' (' || b.postcode || ')' as apartment,
               loc.city_name,
               p.due_date,
               COALESCE(p.payment_date, '-') as payment_date,
               COALESCE(p.amount, 0) as paid_amount,
               l.Agreed_rent,
               CASE
                 WHEN p.payment_date IS NULL THEN 'Unpaid'
                 WHEN p.amount < l.Agreed_rent THEN 'Pending (Partial)'
                 ELSE 'Fully Paid'
               END as status,
               p.is_late,
               p.payment_id
        FROM Payment p
        JOIN Lease l ON p.lease_id = l.lease_id
        JOIN Tenant t ON l.tenant_id = t.tenant_id
        JOIN User u ON t.user_id = u.user_id
        JOIN Apartments a ON l.apartment_id = a.apartment_id
        JOIN Buildings b ON a.building_id = b.building_id
        JOIN Location loc ON b.city_id = loc.city_id
        {where_clause}
        ORDER BY p.due_date DESC, p.payment_id DESC
        """,
        tuple(params)
    )


def get_payment_details(payment_id, user_info=None, city_id=None):
    """Fetch details for a single payment row."""
    update_late_status()
    ensure_tenant_contact_schema()

    scope_city_id = _resolve_finance_scope_city_id(user_info=user_info, city_id=city_id)
    params = [payment_id]
    city_clause = ""

    if scope_city_id is not None:
        city_clause = " AND b.city_id = ?"
        params.append(scope_city_id)

    r = execute_query(
        f"""
        SELECT p.payment_id,
               u.first_name || ' ' || u.surname,
               t.email,
               b.street,
               b.postcode,
               loc.city_name,
               p.due_date,
               COALESCE(p.payment_date, 'N/A'),
               COALESCE(p.amount, 0),
               l.Agreed_rent,
               p.is_late,
               CASE
                 WHEN p.payment_date IS NULL THEN 'Unpaid'
                 WHEN p.amount < l.Agreed_rent THEN 'Pending (Partial)'
                 ELSE 'Fully Paid'
               END as status
        FROM Payment p
        JOIN Lease l ON p.lease_id = l.lease_id
        JOIN Tenant t ON l.tenant_id = t.tenant_id
        JOIN User u ON t.user_id = u.user_id
        JOIN Apartments a ON l.apartment_id = a.apartment_id
        JOIN Buildings b ON a.building_id = b.building_id
        JOIN Location loc ON b.city_id = loc.city_id
        WHERE p.payment_id = ?
        {city_clause}
        """,
        tuple(params),
        'one'
    )

    if not r:
        return None

    return {
        "payment_id": r[0],
        "tenant_name": r[1],
        "tenant_email": r[2],
        "street": r[3],
        "postcode": r[4],
        "city": r[5],
        "due_date": r[6],
        "payment_date": r[7],
        "paid_amount": float(r[8] or 0),
        "agreed_rent": float(r[9] or 0),
        "is_late": r[10],
        "status": r[11],
        "property": f"{r[3]}, {r[4]}",
    }