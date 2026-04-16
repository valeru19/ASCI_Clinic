-- Демо-наполнение БД для UI: ФИО, специализации, записи, визиты, диагнозы.
-- Идемпотентно: повторный запуск не дублирует данные.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS clinic;

ALTER TABLE clinic.doctors
    ADD COLUMN IF NOT EXISTS last_name varchar(100),
    ADD COLUMN IF NOT EXISTS first_name varchar(100),
    ADD COLUMN IF NOT EXISTS middle_name varchar(100),
    ADD COLUMN IF NOT EXISTS monthly_salary numeric(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS bonus_percent numeric(5,2) NOT NULL DEFAULT 0;

INSERT INTO clinic.specialties (name) VALUES
  ('Терапевт'),
  ('Педиатр'),
  ('Хирург'),
  ('ЛОР'),
  ('Кардиолог'),
  ('Невролог')
ON CONFLICT (name) DO NOTHING;

INSERT INTO clinic.icd10_codes (code, title) VALUES
  ('J06.9', 'Острая инфекция верхних дыхательных путей неуточненная'),
  ('K35.9', 'Острый аппендицит неуточненный'),
  ('I10', 'Эссенциальная гипертензия'),
  ('M54.5', 'Боль в пояснице')
ON CONFLICT (code) DO NOTHING;

INSERT INTO clinic.users (id, username, email, password_hash, role, is_active) VALUES
  ('11111111-1111-1111-1111-111111111111', 'doctor_ivanov', 'doctor_ivanov@clinic.local', crypt('doctor12345', gen_salt('bf')), 'doctor', true),
  ('22222222-2222-2222-2222-222222222222', 'doctor_petrova', 'doctor_petrova@clinic.local', crypt('doctor12345', gen_salt('bf')), 'doctor', true),
  ('33333333-3333-3333-3333-333333333333', 'registrar_smirnova', 'registrar_smirnova@clinic.local', crypt('registrar12345', gen_salt('bf')), 'registrar', true)
ON CONFLICT (username) DO NOTHING;

INSERT INTO clinic.doctors (
  id, user_id, license_number, experience_years, last_name, first_name, middle_name, monthly_salary, bonus_percent, is_active
) VALUES
  ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', 'LIC-100001', 12, 'Иванов', 'Иван', 'Иванович', 160000, 20, true),
  ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '22222222-2222-2222-2222-222222222222', 'LIC-100002', 8, 'Петрова', 'Елена', 'Алексеевна', 145000, 15, true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO clinic.doctor_specialties (doctor_id, specialty_id)
SELECT 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, s.id
FROM clinic.specialties s
WHERE s.name IN ('Терапевт', 'Кардиолог')
ON CONFLICT (doctor_id, specialty_id) DO NOTHING;

INSERT INTO clinic.doctor_specialties (doctor_id, specialty_id)
SELECT 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid, s.id
FROM clinic.specialties s
WHERE s.name IN ('Педиатр', 'ЛОР')
ON CONFLICT (doctor_id, specialty_id) DO NOTHING;

INSERT INTO clinic.patients (
  id, last_name, first_name, middle_name, birth_date, gender, phone, email, insurance_number, address, is_active
) VALUES
  ('90000000-0000-0000-0000-000000000001', 'Сидоров', 'Павел', 'Андреевич', '1990-02-12', 'M', '+7 999 100-00-01', 'sidorov@demo.local', 'INS-100001', 'г. Москва, ул. Ленина, 1', true),
  ('90000000-0000-0000-0000-000000000002', 'Кузнецова', 'Мария', 'Игоревна', '1987-09-24', 'F', '+7 999 100-00-02', 'kuznetsova@demo.local', 'INS-100002', 'г. Москва, ул. Тверская, 15', true),
  ('90000000-0000-0000-0000-000000000003', 'Орлов', 'Дмитрий', 'Сергеевич', '2001-01-05', 'M', '+7 999 100-00-03', 'orlov@demo.local', 'INS-100003', 'г. Москва, ул. Арбат, 22', true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO clinic.schedules (id, doctor_id, weekday, start_time, end_time, slot_minutes, is_active) VALUES
  ('70000000-0000-0000-0000-000000000001', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 1, '09:00', '15:00', 30, true),
  ('70000000-0000-0000-0000-000000000002', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 2, '10:00', '16:00', 30, true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO clinic.schedule_slots (id, schedule_id, start_at, end_at, status) VALUES
  ('80000000-0000-0000-0000-000000000001', '70000000-0000-0000-0000-000000000001', now() - interval '4 day', now() - interval '4 day' + interval '30 minute', 'booked'),
  ('80000000-0000-0000-0000-000000000002', '70000000-0000-0000-0000-000000000001', now() + interval '1 day', now() + interval '1 day' + interval '30 minute', 'available'),
  ('80000000-0000-0000-0000-000000000003', '70000000-0000-0000-0000-000000000002', now() + interval '2 day', now() + interval '2 day' + interval '30 minute', 'available')
ON CONFLICT (id) DO NOTHING;

INSERT INTO clinic.appointments (id, slot_id, patient_id, doctor_id, status, reason, created_at, updated_at) VALUES
  ('60000000-0000-0000-0000-000000000001', '80000000-0000-0000-0000-000000000001', '90000000-0000-0000-0000-000000000001', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'completed', 'Боль в горле и температура', now() - interval '4 day', now() - interval '3 day'),
  ('60000000-0000-0000-0000-000000000002', '80000000-0000-0000-0000-000000000002', '90000000-0000-0000-0000-000000000002', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'planned', 'Плановый осмотр', now(), now()),
  ('60000000-0000-0000-0000-000000000003', '80000000-0000-0000-0000-000000000003', '90000000-0000-0000-0000-000000000003', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'planned', 'Консультация ЛОР', now(), now())
ON CONFLICT (id) DO NOTHING;

INSERT INTO clinic.visits (id, appointment_id, chief_complaint, exam_notes, treatment_plan, visit_status, closed_at) VALUES
  ('50000000-0000-0000-0000-000000000001', '60000000-0000-0000-0000-000000000001', 'Боль в горле 3 дня', 'Гиперемия зева, температура 37.8', 'Покой, теплое питье, симптоматическая терапия', 'completed', now() - interval '3 day')
ON CONFLICT (id) DO NOTHING;

INSERT INTO clinic.diagnoses (id, visit_id, icd10_code, is_primary, comment) VALUES
  ('40000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000001', 'J06.9', true, 'Острый процесс, без осложнений')
ON CONFLICT (id) DO NOTHING;

-- Backfill существующих врачей без ФИО/специализаций (например, из старых тестовых данных).
DO $$
DECLARE
  base_specialty_id int;
BEGIN
  SELECT id INTO base_specialty_id FROM clinic.specialties WHERE name = 'Терапевт' LIMIT 1;

  WITH unnamed AS (
    SELECT
      d.id,
      row_number() OVER (ORDER BY d.created_at NULLS LAST, d.id) AS rn
    FROM clinic.doctors d
    WHERE COALESCE(NULLIF(TRIM(COALESCE(d.last_name, '') || ' ' || COALESCE(d.first_name, '')), ''), '') = ''
  )
  UPDATE clinic.doctors d
  SET
    last_name = CASE (u.rn % 8)
      WHEN 1 THEN 'Смирнов'
      WHEN 2 THEN 'Козлов'
      WHEN 3 THEN 'Новиков'
      WHEN 4 THEN 'Морозов'
      WHEN 5 THEN 'Волков'
      WHEN 6 THEN 'Соколов'
      WHEN 7 THEN 'Лебедев'
      ELSE 'Семенов'
    END,
    first_name = CASE (u.rn % 8)
      WHEN 1 THEN 'Алексей'
      WHEN 2 THEN 'Николай'
      WHEN 3 THEN 'Денис'
      WHEN 4 THEN 'Андрей'
      WHEN 5 THEN 'Павел'
      WHEN 6 THEN 'Илья'
      WHEN 7 THEN 'Михаил'
      ELSE 'Евгений'
    END,
    middle_name = CASE (u.rn % 8)
      WHEN 1 THEN 'Викторович'
      WHEN 2 THEN 'Игоревич'
      WHEN 3 THEN 'Олегович'
      WHEN 4 THEN 'Сергеевич'
      WHEN 5 THEN 'Петрович'
      WHEN 6 THEN 'Андреевич'
      WHEN 7 THEN 'Дмитриевич'
      ELSE 'Алексеевич'
    END,
    monthly_salary = CASE WHEN d.monthly_salary = 0 THEN 120000 + (u.rn * 3500) ELSE d.monthly_salary END,
    bonus_percent = CASE WHEN d.bonus_percent = 0 THEN 10 + (u.rn % 15) ELSE d.bonus_percent END
  FROM unnamed u
  WHERE d.id = u.id;

  IF base_specialty_id IS NOT NULL THEN
    INSERT INTO clinic.doctor_specialties (doctor_id, specialty_id)
    SELECT d.id, base_specialty_id
    FROM clinic.doctors d
    WHERE NOT EXISTS (
      SELECT 1 FROM clinic.doctor_specialties ds WHERE ds.doctor_id = d.id
    )
    ON CONFLICT (doctor_id, specialty_id) DO NOTHING;
  END IF;
END $$;
