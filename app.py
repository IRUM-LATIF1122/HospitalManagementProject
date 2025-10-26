# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from models import doctor_model, patient_model, appointment_model, billing_model
from database.connection import get_connection
import joblib, os, pandas as pd

app = Flask(__name__)
app.secret_key = "replace_with_secure_key"

# Home: login page
@app.route('/')
def home():
    return render_template('login.html')

from flask import session, redirect, url_for, flash, request
@app.route('/login', methods=['GET'])
def show_login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_connection()
    if not conn:
        flash("Database connection error", "error")
        return redirect(url_for('home'))

    cur = conn.cursor()
    try:
        # ✅ Positional bind variables avoid ORA-01745 errors
        cur.execute(
            "SELECT role, user_id FROM User_Login WHERE username = :1 AND password = :2",
            (username, password)
        )
        row = cur.fetchone()
    finally:
        cur.close()
        conn.close()

    if row:
        role, user_id = row
        session['username'] = username
        session['role'] = role
        session['user_id'] = user_id

        if role.lower() == 'admin':
            return redirect(url_for('dashboard'))
        elif role.lower() == 'doctor':
            session['doctor_user_id'] = user_id
            return redirect(url_for('doctor_dashboard'))
        else:
            flash("Unknown role", "error")
            return redirect(url_for('home'))
    else:
        flash("Invalid credentials", "error")
        return redirect(url_for('home'))


@app.route('/dashboard')
def dashboard():
    # get small stats
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Patient"); patients = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Doctor"); doctors = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Appointment"); appointments = cur.fetchone()[0]
    cur.close(); conn.close()
    return render_template('dashboard.html', patients=patients, doctors=doctors, appointments=appointments)


@app.route('/doctor/dashboard')
def doctor_dashboard():
    from flask import session
    user_id = session.get('doctor_user_id')
    if not user_id:
        flash("Unauthorized access", "error")
        return redirect(url_for('home'))

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Fetch doctor_id linked to this user (use positional bind)
        cur.execute("SELECT doctor_id, name FROM Doctor WHERE user_id = :1", (user_id,))
        doc_row = cur.fetchone()

        if not doc_row:
            flash("Doctor record not found", "error")
            return redirect(url_for('home'))

        doctor_id, doctor_name = doc_row

        # Fetch doctor’s own appointments (positional bind again)
        cur.execute("""
            SELECT a.appointment_id, p.name, a.appointment_date, a.appointment_time, a.status
            FROM Appointment a
            JOIN Patient p ON a.patient_id = p.patient_id
            WHERE a.doctor_id = :1
            ORDER BY a.appointment_date, a.appointment_time
        """, (doctor_id,))

        appointments = cur.fetchall()

        return render_template('doctor_dashboard.html', doctor_name=doctor_name, appointments=appointments)

    except Exception as e:
        conn.rollback()
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('home'))

    finally:
        cur.close()
        conn.close()



# @app.route('/doctors')
# def doctors():
#     conn = get_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT doctor_id, name, specialization, experience, contact, email FROM Doctor ORDER BY doctor_id")
#     doctors = cur.fetchall()
#     cur.close()
#     conn.close()
#     return render_template('doctor.html', doctors=doctors)
@app.route('/doctors', methods=['GET', 'POST'])
def doctors():
    conn = get_connection()
    cur = conn.cursor()

    search_query = ""
    doctors = []

    if request.method == 'POST':
        search_query = request.form.get('search', '').strip()

        if search_query:
            # ✅ Oracle uses :1 instead of %s
            cur.execute("""
                SELECT doctor_id, name, specialization, experience, contact, email
                FROM Doctor
                WHERE LOWER(name) LIKE LOWER(:1)
                ORDER BY doctor_id
            """, [f"%{search_query}%"])
        else:
            cur.execute("""
                SELECT doctor_id, name, specialization, experience, contact, email
                FROM Doctor
                ORDER BY doctor_id
            """)
    else:
        cur.execute("""
            SELECT doctor_id, name, specialization, experience, contact, email
            FROM Doctor
            ORDER BY doctor_id
        """)

    doctors = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('doctor.html', doctors=doctors, search=search_query)



@app.route('/doctor/add', methods=['POST'])
def doctor_add():
    form = request.form
    name = form['name']
    specialization = form['specialization']
    experience = form.get('experience') or None
    contact = form.get('contact')
    email = form.get('email')
    username = form['username']
    password = form['password']

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Step 1: Insert into User_Login and get new user_id
        cur.execute("""
            INSERT INTO User_Login (user_id, username, password, role, email)
            VALUES (user_seq.NEXTVAL, :u, :p, 'Doctor', :e)
        """, {'u': username, 'p': password, 'e': email})

        # Fetch the latest user_id (from the sequence)
        cur.execute("SELECT user_seq.CURRVAL FROM dual")
        user_id = cur.fetchone()[0]

        # Step 2: Insert into Doctor linked with that user_id
        cur.execute("""
            INSERT INTO Doctor (doctor_id, name, specialization, experience, contact, email, user_id)
            VALUES (doctor_seq.NEXTVAL, :1, :2, :3, :4, :5, :6)
        """, (name, specialization, experience, contact, email, user_id))

        conn.commit()
        flash("Doctor and login created successfully!", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for('doctors'))

# Patients pages
@app.route('/doctor/delete/<int:doctor_id>')
def delete_doctor(doctor_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Fetch user_id of doctor
        cur.execute("SELECT user_id FROM doctor WHERE doctor_id = :did", {"did": doctor_id})
        row = cur.fetchone()
        if not row:
            flash("Doctor not found in database!", "error")
            return redirect(url_for('doctors'))

        user_id = row[0]

        # Delete child records first
        cur.execute("DELETE FROM appointment WHERE doctor_id = :did", {"did": doctor_id})
        cur.execute("DELETE FROM billing WHERE doctor_id = :did", {"did": doctor_id})

        # Delete doctor record
        cur.execute("DELETE FROM doctor WHERE doctor_id = :did", {"did": doctor_id})

        # Delete related user login if exists
        if user_id:
            cur.execute("DELETE FROM user_login WHERE user_id = :uid", {"uid": user_id})

        conn.commit()
        flash("Doctor deleted successfully!", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error deleting doctor: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for('doctors'))


@app.route('/patients', methods=['GET', 'POST'])
def patients():
    conn = get_connection()
    cur = conn.cursor()

    search_query = ""
    patients = []

    if request.method == 'POST':
        search_query = request.form.get('search', '').strip()

        if search_query:
            # 🔍 Search patients by name
            cur.execute("""
                SELECT patient_id, name, age, gender, contact, address, medical_history
                FROM Patient
                WHERE LOWER(name) LIKE LOWER(:1)
                ORDER BY patient_id
            """, [f"%{search_query}%"])
        else:
            # 🧾 Show all patients if search box empty
            cur.execute("""
                SELECT patient_id, name, age, gender, contact, address, medical_history
                FROM Patient
                ORDER BY patient_id
            """)
    else:
        # 🧾 On page load — show all patients
        cur.execute("""
            SELECT patient_id, name, age, gender, contact, address, medical_history
            FROM Patient
            ORDER BY patient_id
        """)

    patients = cur.fetchall()
    cur.close()
    conn.close()

    # 🚫 Show message if no results found
    no_results = (len(patients) == 0)

    return render_template(
        'patient.html',
        patients=patients,
        search=search_query,
        no_results=no_results
    )

@app.route('/patient/add', methods=['POST'])
def patient_add():
    f = request.form
    patient_model.add_patient(f['name'], f.get('age') or None, f.get('gender'), f.get('contact'), f.get('address'), f.get('medical_history'))
    flash("Patient added", "success")
    return redirect(url_for('patients'))

# Appointments
@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    search = None
    no_results = False

    if request.method == 'POST':
        search = request.form.get('search', '').strip()
        if search:
            conn = get_connection()
            cur = conn.cursor()
            query = """
                SELECT a.appointment_id, a.patient_id, p.name AS patient_name,
                       a.doctor_id, d.name AS doctor_name,
                       a.appointment_date, a.appointment_time, a.status
                FROM Appointment a
                JOIN Patient p ON a.patient_id = p.patient_id
                JOIN Doctor d ON a.doctor_id = d.doctor_id
                WHERE LOWER(p.name) LIKE :search OR LOWER(d.name) LIKE :search
                ORDER BY a.appointment_date DESC
            """
            cur.execute(query, {'search': f'%{search.lower()}%'})
            rows = cur.fetchall()
            cur.close()
            conn.close()

            if not rows:
                no_results = True
        else:
            rows = appointment_model.fetch_all_appointments()
    else:
        rows = appointment_model.fetch_all_appointments()

    return render_template(
        'appointment.html',
        appointments=rows,
        search=search,
        no_results=no_results
    )


@app.route('/appointment/add', methods=['POST'])
def appointment_add():
    f = request.form
    appointment_model.add_appointment(f['patient_id'], f['doctor_id'], f['appointment_date'], f['appointment_time'])
    flash("Appointment added", "success")
    return redirect(url_for('appointments'))

@app.route('/appointment/status/<int:appointment_id>', methods=['POST'])
def appointment_status(appointment_id):
    status = request.form.get('status')
    appointment_model.update_appointment_status(appointment_id, status)
    flash("Status updated", "success")
    return redirect(url_for('appointments'))

# Billing
@app.route('/billing', methods=['GET', 'POST'])
def billing():
    search = None
    no_results = False

    if request.method == 'POST':
        search = request.form.get('search', '').strip()
        if search:
            conn = get_connection()
            cur = conn.cursor()

            query = """
                SELECT b.bill_id, b.patient_id, p.name AS patient_name,
                       b.appointment_id, b.amount, b.payment_status, b.billing_date
                FROM Billing b
                JOIN Patient p ON b.patient_id = p.patient_id
                WHERE LOWER(p.name) LIKE :search
                ORDER BY b.bill_id DESC
            """

            cur.execute(query, {'search': f'%{search.lower()}%'})
            bills = cur.fetchall()
            cur.close()
            conn.close()

            if not bills:
                no_results = True
        else:
            bills = billing_model.fetch_all_bills()
    else:
        bills = billing_model.fetch_all_bills()

    return render_template(
        'billing.html',
        bills=bills,
        search=search,
        no_results=no_results
    )


@app.route('/billing/add', methods=['POST'])
def billing_add():
    f = request.form
    try:
        patient_id = int(f['patient_id'])
        appointment_id = int(f['appointment_id'])
        amount = float(f['amount'])
        payment_status = f.get('payment_status', 'Pending')

        billing_model.add_bill(patient_id, appointment_id, amount, payment_status)
        flash("Bill created successfully!", "success")
    except ValueError:
        flash("Invalid input: please enter numeric values for IDs and amount.", "error")
    except Exception as e:
        flash(f"Error creating bill: {str(e)}", "error")

    return redirect(url_for('billing'))


from flask import session, redirect, url_for, flash

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
