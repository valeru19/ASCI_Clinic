CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS clinic;

DO $$
BEGIN
    CREATE TYPE clinic.user_role AS ENUM ('admin', 'doctor', 'registrar', 'patient');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE clinic.gender_enum AS ENUM ('M', 'F', 'O');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE clinic.slot_status AS ENUM ('available', 'booked', 'blocked', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE clinic.appointment_status AS ENUM ('planned', 'confirmed', 'cancelled', 'completed', 'no_show');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE clinic.visit_status AS ENUM ('in_progress', 'completed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE clinic.lab_order_status AS ENUM ('created', 'in_progress', 'completed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE clinic.invoice_status AS ENUM ('draft', 'issued', 'paid', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS clinic.users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    username varchar(100) NOT NULL UNIQUE,
    email varchar(255) NOT NULL UNIQUE,
    password_hash varchar(255) NOT NULL,
    role clinic.user_role NOT NULL,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS clinic.patients (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid UNIQUE REFERENCES clinic.users(id) ON DELETE SET NULL,
    last_name varchar(100) NOT NULL,
    first_name varchar(100) NOT NULL,
    middle_name varchar(100),
    birth_date date NOT NULL,
    gender clinic.gender_enum NOT NULL,
    phone varchar(20),
    insurance_number varchar(50),
    address text,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS clinic.doctors (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid UNIQUE REFERENCES clinic.users(id) ON DELETE SET NULL,
    license_number varchar(50) NOT NULL UNIQUE,
    experience_years smallint NOT NULL CHECK (experience_years >= 0),
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS clinic.specialties (
    id serial PRIMARY KEY,
    name varchar(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS clinic.doctor_specialties (
    doctor_id uuid NOT NULL REFERENCES clinic.doctors(id) ON DELETE CASCADE,
    specialty_id int NOT NULL REFERENCES clinic.specialties(id) ON DELETE RESTRICT,
    PRIMARY KEY (doctor_id, specialty_id)
);

CREATE TABLE IF NOT EXISTS clinic.schedules (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_id uuid NOT NULL REFERENCES clinic.doctors(id) ON DELETE CASCADE,
    weekday smallint NOT NULL CHECK (weekday BETWEEN 1 AND 7),
    start_time time NOT NULL,
    end_time time NOT NULL,
    slot_minutes smallint NOT NULL CHECK (slot_minutes IN (15, 30, 60)),
    is_active boolean NOT NULL DEFAULT true,
    CHECK (end_time > start_time)
);

CREATE TABLE IF NOT EXISTS clinic.schedule_slots (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id uuid NOT NULL REFERENCES clinic.schedules(id) ON DELETE CASCADE,
    start_at timestamptz NOT NULL,
    end_at timestamptz NOT NULL,
    status clinic.slot_status NOT NULL DEFAULT 'available',
    CHECK (end_at > start_at)
);

CREATE TABLE IF NOT EXISTS clinic.appointments (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    slot_id uuid NOT NULL UNIQUE REFERENCES clinic.schedule_slots(id) ON DELETE RESTRICT,
    patient_id uuid NOT NULL REFERENCES clinic.patients(id) ON DELETE RESTRICT,
    doctor_id uuid NOT NULL REFERENCES clinic.doctors(id) ON DELETE RESTRICT,
    status clinic.appointment_status NOT NULL DEFAULT 'planned',
    reason text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS clinic.visits (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_id uuid NOT NULL UNIQUE REFERENCES clinic.appointments(id) ON DELETE CASCADE,
    chief_complaint text NOT NULL,
    exam_notes text NOT NULL,
    treatment_plan text,
    visit_status clinic.visit_status NOT NULL DEFAULT 'in_progress',
    closed_at timestamptz
);

CREATE TABLE IF NOT EXISTS clinic.icd10_codes (
    code varchar(10) PRIMARY KEY,
    title varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS clinic.diagnoses (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id uuid NOT NULL REFERENCES clinic.visits(id) ON DELETE CASCADE,
    icd10_code varchar(10) NOT NULL REFERENCES clinic.icd10_codes(code) ON DELETE RESTRICT,
    is_primary boolean NOT NULL DEFAULT false,
    comment text
);

CREATE TABLE IF NOT EXISTS clinic.medications (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name varchar(150) NOT NULL,
    form varchar(50),
    strength varchar(50),
    atc_code varchar(20)
);

CREATE TABLE IF NOT EXISTS clinic.prescriptions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id uuid NOT NULL REFERENCES clinic.visits(id) ON DELETE CASCADE,
    medication_id uuid NOT NULL REFERENCES clinic.medications(id) ON DELETE RESTRICT,
    dosage varchar(100) NOT NULL,
    frequency varchar(100) NOT NULL,
    duration_days smallint NOT NULL CHECK (duration_days > 0 AND duration_days <= 365),
    instructions text
);

CREATE TABLE IF NOT EXISTS clinic.lab_test_types (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code varchar(30) NOT NULL UNIQUE,
    name varchar(150) NOT NULL,
    unit varchar(30),
    reference_range varchar(100)
);

CREATE TABLE IF NOT EXISTS clinic.lab_orders (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id uuid NOT NULL REFERENCES clinic.visits(id) ON DELETE CASCADE,
    patient_id uuid NOT NULL REFERENCES clinic.patients(id) ON DELETE RESTRICT,
    ordered_by_doctor_id uuid NOT NULL REFERENCES clinic.doctors(id) ON DELETE RESTRICT,
    status clinic.lab_order_status NOT NULL DEFAULT 'created',
    ordered_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS clinic.lab_order_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_order_id uuid NOT NULL REFERENCES clinic.lab_orders(id) ON DELETE CASCADE,
    test_type_id uuid NOT NULL REFERENCES clinic.lab_test_types(id) ON DELETE RESTRICT,
    priority varchar(20) NOT NULL DEFAULT 'normal'
);

CREATE TABLE IF NOT EXISTS clinic.lab_results (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_order_item_id uuid NOT NULL UNIQUE REFERENCES clinic.lab_order_items(id) ON DELETE CASCADE,
    value_text varchar(100),
    value_numeric numeric(10, 2),
    unit varchar(30),
    reference_range varchar(50),
    flag varchar(10),
    resulted_at timestamptz NOT NULL DEFAULT now(),
    validated_by_doctor_id uuid REFERENCES clinic.doctors(id) ON DELETE SET NULL,
    CHECK (value_text IS NOT NULL OR value_numeric IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS clinic.services (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code varchar(30) NOT NULL UNIQUE,
    name varchar(150) NOT NULL,
    price numeric(12, 2) NOT NULL CHECK (price >= 0),
    is_active boolean NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS clinic.invoices (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id uuid NOT NULL REFERENCES clinic.patients(id) ON DELETE RESTRICT,
    appointment_id uuid REFERENCES clinic.appointments(id) ON DELETE SET NULL,
    status clinic.invoice_status NOT NULL DEFAULT 'draft',
    total_amount numeric(12, 2) NOT NULL CHECK (total_amount >= 0),
    issued_at timestamptz NOT NULL DEFAULT now(),
    due_at timestamptz
);

CREATE TABLE IF NOT EXISTS clinic.invoice_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id uuid NOT NULL REFERENCES clinic.invoices(id) ON DELETE CASCADE,
    service_id uuid NOT NULL REFERENCES clinic.services(id) ON DELETE RESTRICT,
    qty int NOT NULL CHECK (qty > 0),
    unit_price numeric(12, 2) NOT NULL CHECK (unit_price >= 0),
    total_price numeric(12, 2) NOT NULL CHECK (total_price >= 0)
);

CREATE TABLE IF NOT EXISTS clinic.audit_log (
    id bigserial PRIMARY KEY,
    table_name varchar(100) NOT NULL,
    record_id uuid NOT NULL,
    operation varchar(10) NOT NULL,
    changed_by uuid REFERENCES clinic.users(id) ON DELETE SET NULL,
    changed_at timestamptz NOT NULL DEFAULT now(),
    before_data jsonb,
    after_data jsonb
);

CREATE INDEX IF NOT EXISTS idx_patients_name_birth
    ON clinic.patients (last_name, first_name, birth_date);

CREATE INDEX IF NOT EXISTS idx_appointments_doctor_status
    ON clinic.appointments (doctor_id, status, created_at);

CREATE INDEX IF NOT EXISTS idx_schedule_slots_time
    ON clinic.schedule_slots (schedule_id, start_at, end_at);

CREATE INDEX IF NOT EXISTS idx_lab_orders_patient_time
    ON clinic.lab_orders (patient_id, ordered_at);

CREATE INDEX IF NOT EXISTS idx_invoices_patient_status
    ON clinic.invoices (patient_id, status, issued_at);

INSERT INTO clinic.users (username, email, password_hash, role, is_active)
VALUES (
    'admin',
    'admin@clinic.local',
    crypt('admin12345', gen_salt('bf')),
    'admin',
    true
)
ON CONFLICT (username) DO NOTHING;
