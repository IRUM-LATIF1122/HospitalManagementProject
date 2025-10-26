# models/billing_model.py
from database.connection import get_connection

def fetch_all_bills():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT b.bill_id, b.patient_id, p.name, b.appointment_id, b.amount, b.payment_status, b.billing_date
        FROM Billing b JOIN Patient p ON b.patient_id = p.patient_id
        ORDER BY b.billing_date DESC
    """)
    rows = cur.fetchall(); cur.close(); conn.close(); return rows

def add_bill(patient_id, appointment_id, amount, payment_status='Pending'):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO Billing (patient_id, appointment_id, amount, payment_status, billing_date) VALUES (:1,:2,:3,:4,SYSDATE)",
                (patient_id, appointment_id, amount, payment_status))
    conn.commit(); cur.close(); conn.close()
