# models/appointment_model.py
from database.connection import get_connection
from datetime import datetime

def fetch_all_appointments():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT a.appointment_id, a.patient_id, p.name, a.doctor_id, d.name, a.appointment_date, a.appointment_time, a.status
        FROM Appointment a
        JOIN Patient p ON a.patient_id = p.patient_id
        JOIN Doctor d ON a.doctor_id = d.doctor_id
        ORDER BY a.appointment_date, a.appointment_time
    """)
    rows = cur.fetchall(); cur.close(); conn.close(); return rows

# def add_appointment(patient_id, doctor_id, appointment_date, appointment_time, status='Scheduled'):
#     conn = get_connection(); cur = conn.cursor()
#     cur.execute("""
#         INSERT INTO Appointment (patient_id, doctor_id, appointment_date, appointment_time, status)
#         VALUES (:1,:2,TO_DATE(:3,'YYYY-MM-DD'),:4,:5)
#     """, (patient_id, doctor_id, appointment_date, appointment_time, status))
#     conn.commit(); cur.close(); conn.close()



def add_appointment(patient_id, doctor_id, appointment_date, appointment_time, status='Scheduled'):
    # Normalize date string to datetime object
    try:
        # Handles both 'YYYY-MM-DD' and 'YYYY-MM-DDTHH:MM'
        appointment_date = appointment_date.split('T')[0]
        appointment_date_obj = datetime.strptime(appointment_date, "%Y-%m-%d")
    except ValueError:
        # If user enters different format, raise readable error
        raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Appointment (patient_id, doctor_id, appointment_date, appointment_time, status)
        VALUES (:1, :2, :3, :4, :5)
    """, (patient_id, doctor_id, appointment_date_obj, appointment_time, status))
    conn.commit()
    cur.close()
    conn.close()



def update_appointment_status(appointment_id, status):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("UPDATE Appointment SET status=:1 WHERE appointment_id=:2", (status, appointment_id))
    conn.commit(); cur.close(); conn.close()

def delete_appointment(appointment_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM Appointment WHERE appointment_id=:id", {"id": appointment_id})
    conn.commit(); cur.close(); conn.close()
