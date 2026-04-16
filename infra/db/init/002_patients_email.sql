-- Дополнительное поле для соответствия API и ТЗ (контакты пациента).
ALTER TABLE clinic.patients
    ADD COLUMN IF NOT EXISTS email varchar(255);
