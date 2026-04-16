CREATE TABLE IF NOT EXISTS clinic.schedule_exceptions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_id uuid NOT NULL REFERENCES clinic.doctors(id) ON DELETE CASCADE,
    date_from date NOT NULL,
    date_to date NOT NULL,
    reason varchar(255) NOT NULL,
    CHECK (date_to >= date_from)
);
