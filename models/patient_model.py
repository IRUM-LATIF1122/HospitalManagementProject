# models/patient_model.py
from database.connection import get_connection

def fetch_all_patients():
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    cur.execute("SELECT patient_id, name, age, gender, contact, address, medical_history FROM Patient ORDER BY patient_id")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows

def get_patient(patient_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT patient_id, name, age, gender, contact, address, medical_history FROM Patient WHERE patient_id=:id", {"id": patient_id})
    r = cur.fetchone(); cur.close(); conn.close(); return r

def add_patient(name, age, gender, contact, address, medical_history):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO Patient (name, age, gender, contact, address, medical_history) VALUES (:1,:2,:3,:4,:5,:6)",
                (name, age, gender, contact, address, medical_history))
    conn.commit(); cur.close(); conn.close()

def update_patient(patient_id, name, age, gender, contact, address, medical_history):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE Patient SET name=:1, age=:2, gender=:3, contact=:4, address=:5, medical_history=:6
        WHERE patient_id=:7
    """, (name, age, gender, contact, address, medical_history, patient_id))
    conn.commit(); cur.close(); conn.close()

def delete_patient(patient_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM Patient WHERE patient_id=:id", {"id": patient_id})
    conn.commit(); cur.close(); conn.close()
