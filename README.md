
# 🏥 Hospital Management System (Flask + OracleDB)

A full-stack **Hospital Management System** built using **Flask** and **Oracle Database**.
It provides a clean web interface for managing **doctors**, **patients**, **appointments**, and **billing**, designed for educational and real-world use.

---

## 🌐 Overview

This project demonstrates a complete CRUD-based hospital management solution with secure authentication, dashboard, and modular database integration.
It aims to help small medical centers manage daily operations efficiently — built as part of a university data management and web development project.

---

## ⚙️ Features

✅ **User Authentication** — Secure login with session management
✅ **Doctor Management** — Add, edit, delete, and view doctors
✅ **Patient Management** — Track patient details and history
✅ **Appointments Module** — Manage and schedule doctor–patient meetings
✅ **Billing System** — Generate and store billing records
✅ **Database Integration** — Uses Oracle Database for backend storage
✅ **Responsive UI** — Built with HTML, CSS, and Flask templates

---

## 🧩 Tech Stack

| Layer              | Technology                     |
| ------------------ | ------------------------------ |
| Backend            | Flask (Python)                 |
| Database           | Oracle Database                |
| Frontend           | HTML5, CSS3, JS                |
| ORM / Logic        | Custom Python models           |
| Hosting (optional) | Flask local server or Gunicorn |

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/IRUM-LATIF1122/HospitalManagementProject.git
cd HospitalManagementProject/Hospital_project
```

### 2️⃣ Create a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux
```

### 3️⃣ Install Dependencies

```bash
pip install flask oracledb pandas joblib
```

### 4️⃣ Configure Database Connection

Edit `database/connection.py`:

```python
import oracledb

def get_connection():
    dsn = oracledb.makedsn("localhost", 1521, service_name="your_service")
    conn = oracledb.connect(user="your_username", password="your_password", dsn=dsn)
    return conn
```

Test the connection:

```bash
python test_db.py
```

### 5️⃣ Run the App

```bash
python app.py
```

Then open your browser at:
👉 `http://127.0.0.1:5000/`

---

## 🗂️ Project Structure

```
Hospital_project/
│
├── app.py                 # Main Flask application
├── test_db.py             # Test database connectivity
│
├── database/
│   └── connection.py      # Oracle DB connection setup
│
├── models/
│   ├── doctor_model.py
│   ├── patient_model.py
│   ├── appointment_model.py
│   └── billing_model.py   # Database CRUD operations
│
├── templates/             # HTML templates
│   ├── login.html
│   ├── dashboard.html
│   ├── doctor.html
│   ├── patient.html
│   ├── appointment.html
│   └── billing.html
│
└── static/                # CSS / JS assets
    ├── css/style.css
    └── js/script.js
```

---

## 💾 Database Tables (Example Schema)

| Table        | Description                         |
| ------------ | ----------------------------------- |
| User_Login   | Stores username, password, and role |
| Doctors      | Doctor profiles and specialties     |
| Patients     | Patient personal and medical info   |
| Appointments | Scheduling data                     |
| Billing      | Payment and invoice records         |

---

## 🖼️ Screenshots (Add Later)

| Page                                    | Description        |
| --------------------------------------- | ------------------ |
| ![login](screenshots/login.png)         | Login Page         |
| ![dashboard](screenshots/dashboard.png) | Dashboard Overview |
| ![doctors](screenshots/doctors.png)     | Doctor Management  |

*(Create a `/screenshots` folder and place images there)*

---

## 🧠 Future Enhancements

* ✅ Add role-based access (Admin/Doctor/Receptionist)
* ✅ Integrate analytics dashboard (using Pandas or Plotly)
* ✅ Add email or SMS notifications
* ✅ Cloud deployment using Render / Railway

---

## 🧑‍💻 Author

**IRUM LATIF**
🎓 BSCS Student | 💻 Aspiring Data Scientist & AI Developer
📫 [GitHub Profile](https://github.com/IRUM-LATIF1122)

