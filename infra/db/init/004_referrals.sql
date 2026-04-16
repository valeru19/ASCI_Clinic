CREATE TABLE IF NOT EXISTS clinic.referrals (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id uuid NOT NULL REFERENCES clinic.visits(id) ON DELETE CASCADE,
    target_specialty_id int NOT NULL REFERENCES clinic.specialties(id) ON DELETE RESTRICT,
    target_doctor_id uuid REFERENCES clinic.doctors(id) ON DELETE SET NULL,
    reason text NOT NULL,
    status varchar(20) NOT NULL DEFAULT 'created',
    comment text,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (status IN ('created', 'accepted', 'rejected', 'completed'))
);
