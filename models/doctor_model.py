# models/doctor_model.py
from database.connection import get_connection

def fetch_all_doctors():
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    cur.execute("SELECT doctor_id, name, specialization, experience, contact, email FROM Doctor ORDER BY doctor_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_doctor(doctor_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT doctor_id, name, specialization, experience, contact, email FROM Doctor WHERE doctor_id = :id", {"id": doctor_id})
    row = cur.fetchone()
    cur.close(); conn.close()
    return row

def add_doctor(name, specialization, experience, contact, email):
    conn = get_connection(); cur = conn.cursor()
    cur.execute(
        "INSERT INTO Doctor (name, specialization, experience, contact, email) VALUES (:1,:2,:3,:4,:5)",
        (name, specialization, experience, contact, email)
    )
    conn.commit(); cur.close(); conn.close()

def update_doctor(doctor_id, name, specialization, experience, contact, email):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE Doctor SET name=:1, specialization=:2, experience=:3, contact=:4, email=:5
        WHERE doctor_id=:6
    """, (name, specialization, experience, contact, email, doctor_id))
    conn.commit(); cur.close(); conn.close()

def delete_doctor(doctor_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM Doctor WHERE doctor_id=:id", {"id": doctor_id})
    conn.commit(); cur.close(); conn.close()
