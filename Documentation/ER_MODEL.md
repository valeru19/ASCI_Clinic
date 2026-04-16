# ER-модель данных АИС "Клиника"

## Диаграмма

Исходник диаграммы:
- `uml/er-clinic.puml`

Диаграмма фиксирует конечный набор сущностей, связи и базовые типы данных для PostgreSQL.

## Ключевые группы сущностей

- **Пользователи и роли:** `users`, `patients`, `doctors`, `specialties`, `doctor_specialties`.
- **Расписание и запись:** `schedules`, `schedule_slots`, `schedule_exceptions`, `appointments`.
- **Медицинская часть:** `visits`, `diagnoses`, `icd10_codes`, `prescriptions`, `medications`, `referrals`.
- **Лаборатория:** `lab_test_types`, `lab_orders`, `lab_order_items`, `lab_results`.
- **Финансы:** `services`, `invoices`, `invoice_items`.
- **Аудит:** `audit_log`.

## Обязательные перечисления (enum)

Рекомендуемые enum-типы в PostgreSQL:

- `user_role`: `admin`, `doctor`, `registrar`, `patient`.
- `gender_enum`: `M`, `F`, `O`.
- `slot_status`: `available`, `booked`, `blocked`, `cancelled`.
- `appointment_status`: `planned`, `confirmed`, `cancelled`, `completed`, `no_show`.
- `visit_status`: `in_progress`, `completed`, `cancelled`.
- `lab_order_status`: `created`, `in_progress`, `completed`, `cancelled`.
- `invoice_status`: `draft`, `issued`, `paid`, `cancelled`.

## Ключевые ограничения целостности

- Связь `users -> patients` и `users -> doctors` формата `1:0..1` через `UNIQUE (user_id)`.
- Один временной слот (`schedule_slots`) может быть использован максимум одной записью (`appointments.slot_id UNIQUE`).
- Один состоявшийся прием (`appointments`) порождает максимум один визит (`visits.appointment_id UNIQUE`).
- Для результата анализа одна строка результата на один пункт назначения (`lab_results.lab_order_item_id UNIQUE`).
- Денежные поля (`price`, `total_amount`) — `numeric(12,2)`.
- Критичные события пишутся в `audit_log` (через триггеры/сервисный слой).

## Минимальные индексы

- `patients(last_name, first_name, birth_date)` + GIN по `search_vector` (при наличии).
- `appointments(doctor_id, status, created_at)`.
- `schedule_slots(schedule_id, start_at, end_at)`.
- `visits(appointment_id)`.
- `diagnoses(icd10_code)`.
- `lab_orders(patient_id, ordered_at)`.
- `invoices(patient_id, issued_at, status)`.

## Нормализация

Модель рассчитана на соблюдение 3НФ:
- справочники вынесены отдельно (`specialties`, `icd10_codes`, `medications`, `services`, `lab_test_types`);
- M:N связи реализованы связующими таблицами (`doctor_specialties`);
- транзитивные зависимости сведены к минимуму.
