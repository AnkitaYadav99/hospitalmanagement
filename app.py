import streamlit as st
from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Smart Hospital Management",
    page_icon="🏥",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
    .main {
        background-color: #f5f7fb;
    }

    .title {
        font-size: 38px;
        font-weight: 700;
        color: #172033;
    }

    .subtitle {
        color: #667085;
        font-size: 17px;
    }

    .card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.08);
        margin-bottom: 15px;
    }

    .emergency {
        background: #fff1f0;
        border-left: 5px solid #e53935;
        padding: 15px;
        border-radius: 10px;
    }

    .normal {
        background: #f0f9ff;
        border-left: 5px solid #2196f3;
        padding: 15px;
        border-radius: 10px;
    }

    .success {
        background: #effaf3;
        border-left: 5px solid #22c55e;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# ABSTRACT CLASS - PERSON
# =========================================================

class Person(ABC):

    def __init__(self, name, age, gender):
        self.__name = name
        self.__age = age
        self.__gender = gender

    # Encapsulation using getters
    def get_name(self):
        return self.__name

    def get_age(self):
        return self.__age

    def get_gender(self):
        return self.__gender

    @abstractmethod
    def get_role(self):
        pass


# =========================================================
# PATIENT CLASS
# =========================================================

class Patient(Person):

    patient_counter = 1000

    def __init__(self, name, age, gender, disease):
        super().__init__(name, age, gender)

        Patient.patient_counter += 1

        self.patient_id = "P" + str(Patient.patient_counter)
        self.disease = disease
        self.status = "Waiting"

    def get_role(self):
        return "Patient"

    def update_status(self, status):
        self.status = status


# =========================================================
# DOCTOR CLASS
# =========================================================

class Doctor(Person):

    doctor_counter = 200

    def __init__(self, name, age, gender, specialization):
        super().__init__(name, age, gender)

        Doctor.doctor_counter += 1

        self.doctor_id = "D" + str(Doctor.doctor_counter)
        self.specialization = specialization
        self.available = True

    def get_role(self):
        return "Doctor"

    def check_availability(self):
        return self.available

    def change_availability(self, status):
        self.available = status


# =========================================================
# EMERGENCY CASE
# =========================================================

class EmergencyCase:

    def __init__(self, patient, emergency_type, severity):
        self.patient = patient
        self.emergency_type = emergency_type
        self.severity = severity
        self.time = datetime.now()

    # Polymorphism
    def calculate_priority(self):
        if self.severity == "Critical":
            return 1
        elif self.severity == "Serious":
            return 2
        else:
            return 3


# =========================================================
# APPOINTMENT CLASS
# =========================================================

class Appointment:

    appointment_counter = 500

    def __init__(self, patient, doctor, date, time):
        Appointment.appointment_counter += 1

        self.appointment_id = "A" + str(Appointment.appointment_counter)
        self.patient = patient
        self.doctor = doctor
        self.date = date
        self.time = time
        self.status = "Scheduled"


# =========================================================
# HOSPITAL MANAGEMENT SYSTEM
# =========================================================

class Hospital:

    def __init__(self):

        self.patients = []
        self.doctors = []
        self.appointments = []
        self.emergency_cases = []

        self.total_beds = 50
        self.available_beds = 32

        self.medicines = {
            "Paracetamol": 100,
            "Amoxicillin": 50,
            "Insulin": 30,
            "Painkiller": 70,
            "Antibiotics": 45
        }

    # -------------------------
    # PATIENT MANAGEMENT
    # -------------------------

    def add_patient(self, patient):
        self.patients.append(patient)

    # -------------------------
    # DOCTOR MANAGEMENT
    # -------------------------

    def add_doctor(self, doctor):
        self.doctors.append(doctor)

    # -------------------------
    # APPOINTMENT
    # -------------------------

    def add_appointment(self, appointment):
        self.appointments.append(appointment)

    # -------------------------
    # EMERGENCY
    # -------------------------

    def add_emergency(self, emergency):
        self.emergency_cases.append(emergency)

        # Allocate bed for critical cases
        if emergency.severity == "Critical" and self.available_beds > 0:
            self.available_beds -= 1
            emergency.patient.update_status("Admitted")

    # -------------------------
    # AVAILABLE DOCTORS
    # -------------------------

    def available_doctors(self):
        return [
            doctor for doctor in self.doctors
            if doctor.check_availability()
        ]


# =========================================================
# SESSION STATE
# =========================================================

if "hospital" not in st.session_state:

    hospital = Hospital()

    # Default doctors
    hospital.add_doctor(
        Doctor(
            "Dr. Raj Sharma",
            45,
            "Male",
            "Cardiologist"
        )
    )

    hospital.add_doctor(
        Doctor(
            "Dr. Priya Mehta",
            39,
            "Female",
            "Neurologist"
        )
    )

    hospital.add_doctor(
        Doctor(
            "Dr. Amit Verma",
            42,
            "Male",
            "General Physician"
        )
    )

    st.session_state.hospital = hospital


hospital = st.session_state.hospital


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🏥 Smart Hospital")

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "👨‍⚕️ Doctors",
        "🧑 Patients",
        "📅 Appointments",
        "🚨 Emergency",
        "💊 Medicine Inventory"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Object-Oriented Smart Hospital "
    "Management System"
)


# =========================================================
# DASHBOARD
# =========================================================

if menu == "📊 Dashboard":

    st.markdown(
        '<div class="title">Smart Hospital Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Hospital management and emergency prioritization system</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "👨‍⚕️ Doctors",
            len(hospital.doctors)
        )

    with col2:
        st.metric(
            "🧑 Patients",
            len(hospital.patients)
        )

    with col3:
        st.metric(
            "📅 Appointments",
            len(hospital.appointments)
        )

    with col4:
        st.metric(
            "🚨 Emergency Cases",
            len(hospital.emergency_cases)
        )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True
        )

        st.subheader("🛏️ Bed Availability")

        st.progress(
            hospital.available_beds /
            hospital.total_beds
        )

        st.write(
            f"Available Beds: "
            f"**{hospital.available_beds} / {hospital.total_beds}**"
        )

        st.write(
            f"Occupied Beds: "
            f"**{hospital.total_beds - hospital.available_beds}**"
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True
        )

        st.subheader("🚨 Emergency Overview")

        critical = len([
            x for x in hospital.emergency_cases
            if x.severity == "Critical"
        ])

        serious = len([
            x for x in hospital.emergency_cases
            if x.severity == "Serious"
        ])

        normal = len([
            x for x in hospital.emergency_cases
            if x.severity == "Normal"
        ])

        st.write(f"🔴 Critical: **{critical}**")
        st.write(f"🟠 Serious: **{serious}**")
        st.write(f"🟢 Normal: **{normal}**")

        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# DOCTORS
# =========================================================

elif menu == "👨‍⚕️ Doctors":

    st.title("👨‍⚕️ Doctor Management")

    tab1, tab2 = st.tabs(
        ["Doctor List", "Add Doctor"]
    )

    # -------------------------
    # DOCTOR LIST
    # -------------------------

    with tab1:

        if hospital.doctors:

            data = []

            for doctor in hospital.doctors:

                data.append({
                    "Doctor ID": doctor.doctor_id,
                    "Name": doctor.get_name(),
                    "Age": doctor.get_age(),
                    "Gender": doctor.get_gender(),
                    "Specialization": doctor.specialization,
                    "Available": "Yes"
                    if doctor.available
                    else "No"
                })

            st.dataframe(
                pd.DataFrame(data),
                use_container_width=True
            )

    # -------------------------
    # ADD DOCTOR
    # -------------------------

    with tab2:

        with st.form("doctor_form"):

            name = st.text_input("Doctor Name")
            age = st.number_input(
                "Age",
                min_value=20,
                max_value=80,
                value=30
            )

            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"]
            )

            specialization = st.selectbox(
                "Specialization",
                [
                    "Cardiologist",
                    "Neurologist",
                    "General Physician",
                    "Orthopedic",
                    "Dermatologist",
                    "Pediatrician"
                ]
            )

            submitted = st.form_submit_button(
                "➕ Add Doctor"
            )

            if submitted:

                if name:

                    doctor = Doctor(
                        name,
                        age,
                        gender,
                        specialization
                    )

                    hospital.add_doctor(doctor)

                    st.success(
                        f"Doctor {name} added successfully!"
                    )

                    st.rerun()

                else:
                    st.error(
                        "Please enter doctor name."
                    )


# =========================================================
# PATIENTS
# =========================================================

elif menu == "🧑 Patients":

    st.title("🧑 Patient Management")

    tab1, tab2 = st.tabs(
        ["Patient List", "Register Patient"]
    )

    with tab1:

        if hospital.patients:

            data = []

            for patient in hospital.patients:

                data.append({
                    "Patient ID": patient.patient_id,
                    "Name": patient.get_name(),
                    "Age": patient.get_age(),
                    "Gender": patient.get_gender(),
                    "Disease": patient.disease,
                    "Status": patient.status
                })

            st.dataframe(
                pd.DataFrame(data),
                use_container_width=True
            )

        else:

            st.info(
                "No patients registered yet."
            )

    with tab2:

        with st.form("patient_form"):

            name = st.text_input(
                "Patient Name"
            )

            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                value=20
            )

            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"]
            )

            disease = st.text_input(
                "Disease / Medical Problem"
            )

            submitted = st.form_submit_button(
                "➕ Register Patient"
            )

            if submitted:

                if name and disease:

                    patient = Patient(
                        name,
                        age,
                        gender,
                        disease
                    )

                    hospital.add_patient(patient)

                    st.success(
                        f"Patient registered successfully!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Please fill all fields."
                    )


# =========================================================
# APPOINTMENTS
# =========================================================

elif menu == "📅 Appointments":

    st.title("📅 Appointment Management")

    if not hospital.patients:

        st.warning(
            "Register a patient first."
        )

    elif not hospital.doctors:

        st.warning(
            "Add a doctor first."
        )

    else:

        with st.form("appointment_form"):

            patient_options = {
                p.patient_id:
                p.get_name()
                for p in hospital.patients
            }

            doctor_options = {
                d.doctor_id:
                f"{d.get_name()} - {d.specialization}"
                for d in hospital.doctors
                if d.available
            }

            patient_id = st.selectbox(
                "Select Patient",
                list(patient_options.keys()),
                format_func=lambda x:
                f"{x} - {patient_options[x]}"
            )

            doctor_id = st.selectbox(
                "Select Doctor",
                list(doctor_options.keys()),
                format_func=lambda x:
                f"{x} - {doctor_options[x]}"
            )

            date = st.date_input(
                "Appointment Date"
            )

            time = st.time_input(
                "Appointment Time"
            )

            submitted = st.form_submit_button(
                "📅 Schedule Appointment"
            )

            if submitted:

                patient = next(
                    p for p in hospital.patients
                    if p.patient_id == patient_id
                )

                doctor = next(
                    d for d in hospital.doctors
                    if d.doctor_id == doctor_id
                )

                appointment = Appointment(
                    patient,
                    doctor,
                    date,
                    time
                )

                hospital.add_appointment(
                    appointment
                )

                st.success(
                    "Appointment scheduled successfully!"
                )

                st.rerun()

    st.markdown("---")

    st.subheader("Scheduled Appointments")

    if hospital.appointments:

        data = []

        for appointment in hospital.appointments:

            data.append({
                "Appointment ID":
                    appointment.appointment_id,
                "Patient":
                    appointment.patient.get_name(),
                "Doctor":
                    appointment.doctor.get_name(),
                "Specialization":
                    appointment.doctor.specialization,
                "Date":
                    appointment.date,
                "Time":
                    appointment.time,
                "Status":
                    appointment.status
            })

        st.dataframe(
            pd.DataFrame(data),
            use_container_width=True
        )

    else:

        st.info(
            "No appointments scheduled."
        )


# =========================================================
# EMERGENCY MANAGEMENT
# =========================================================

elif menu == "🚨 Emergency":

    st.title(
        "🚨 Emergency Prioritization"
    )

    if not hospital.patients:

        st.warning(
            "Register a patient before creating an emergency case."
        )

    else:

        with st.form("emergency_form"):

            patient_options = {
                p.patient_id:
                p.get_name()
                for p in hospital.patients
            }

            patient_id = st.selectbox(
                "Select Patient",
                list(patient_options.keys()),
                format_func=lambda x:
                f"{x} - {patient_options[x]}"
            )

            emergency_type = st.selectbox(
                "Emergency Type",
                [
                    "Heart Attack",
                    "Accident",
                    "Breathing Problem",
                    "Stroke",
                    "Severe Injury",
                    "Fever",
                    "Other"
                ]
            )

            severity = st.selectbox(
                "Severity",
                [
                    "Critical",
                    "Serious",
                    "Normal"
                ]
            )

            submitted = st.form_submit_button(
                "🚨 Register Emergency"
            )

            if submitted:

                patient = next(
                    p for p in hospital.patients
                    if p.patient_id == patient_id
                )

                emergency = EmergencyCase(
                    patient,
                    emergency_type,
                    severity
                )

                hospital.add_emergency(
                    emergency
                )

                st.success(
                    "Emergency case registered and prioritized."
                )

                st.rerun()

    st.markdown("---")

    st.subheader(
        "Emergency Priority Queue"
    )

    if hospital.emergency_cases:

        sorted_cases = sorted(
            hospital.emergency_cases,
            key=lambda x: x.calculate_priority()
        )

        data = []

        for case in sorted_cases:

            if case.severity == "Critical":
                priority = "🔴 HIGH"

            elif case.severity == "Serious":
                priority = "🟠 MEDIUM"

            else:
                priority = "🟢 LOW"

            data.append({
                "Priority": priority,
                "Patient ID":
                    case.patient.patient_id,
                "Patient":
                    case.patient.get_name(),
                "Emergency":
                    case.emergency_type,
                "Severity":
                    case.severity,
                "Patient Status":
                    case.patient.status
            })

        st.dataframe(
            pd.DataFrame(data),
            use_container_width=True
        )

    else:

        st.info(
            "No emergency cases registered."
        )


# =========================================================
# MEDICINE INVENTORY
# =========================================================

elif menu == "💊 Medicine Inventory":

    st.title(
        "💊 Medicine Inventory"
    )

    data = []

    for medicine, quantity in hospital.medicines.items():

        if quantity <= 20:
            status = "🔴 Low Stock"

        elif quantity <= 50:
            status = "🟠 Medium"

        else:
            status = "🟢 Available"

        data.append({
            "Medicine": medicine,
            "Quantity": quantity,
            "Status": status
        })

    st.dataframe(
        pd.DataFrame(data),
        use_container_width=True
    )

    st.markdown("---")

    st.subheader(
        "Update Medicine Stock"
    )

    medicine = st.selectbox(
        "Select Medicine",
        list(hospital.medicines.keys())
    )

    quantity = st.number_input(
        "Add Quantity",
        min_value=1,
        max_value=1000,
        value=10
    )

    if st.button(
        "➕ Add Stock"
    ):

        hospital.medicines[medicine] += quantity

        st.success(
            f"{quantity} units of {medicine} added."
        )

        st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "🏥 Smart Hospital Management System | "
    "Built using Python + OOP + Streamlit"
)