-- Идемпотентное создание/обновление демо-администратора.
-- Можно выполнять в любой момент (в отличие от docker-entrypoint-initdb.d при первом создании volume).
-- Требуется расширение pgcrypto (создаётся в 001_init.sql).

INSERT INTO clinic.users (username, email, password_hash, role, is_active)
VALUES (
    'admin',
    'admin@clinic.local',
    crypt('admin12345', gen_salt('bf')),
    'admin',
    true
)
ON CONFLICT (username) DO UPDATE SET
    email = EXCLUDED.email,
    password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    is_active = EXCLUDED.is_active;
