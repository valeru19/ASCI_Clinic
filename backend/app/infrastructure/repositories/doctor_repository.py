from sqlalchemy import text
from sqlalchemy.orm import Session


class SQLAlchemyDoctorRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def ensure_profile_columns(self) -> None:
        self.session.execute(
            text(
                """
                ALTER TABLE clinic.doctors
                ADD COLUMN IF NOT EXISTS last_name varchar(100),
                ADD COLUMN IF NOT EXISTS first_name varchar(100),
                ADD COLUMN IF NOT EXISTS middle_name varchar(100),
                ADD COLUMN IF NOT EXISTS monthly_salary numeric(12,2) NOT NULL DEFAULT 0,
                ADD COLUMN IF NOT EXISTS bonus_percent numeric(5,2) NOT NULL DEFAULT 0
                """
            )
        )

    def _normalize_row(self, row: dict) -> dict:
        full_name = (row.get("full_name") or "").strip()
        row["full_name"] = full_name if full_name else (row.get("username") or "Без ФИО")
        row["specializations"] = list(row.get("specializations") or [])
        row["monthly_salary"] = float(row.get("monthly_salary") or 0)
        row["bonus_percent"] = float(row.get("bonus_percent") or 0)
        return row

    def list_doctors(
        self,
        *,
        include_inactive: bool,
        skip: int,
        limit: int,
    ) -> list[dict]:
        self.ensure_profile_columns()
        filters = ""
        params: dict[str, object] = {"skip": skip, "limit": limit}
        if not include_inactive:
            filters = "WHERE d.is_active = true"

        rows = self.session.execute(
            text(
                f"""
                SELECT
                    d.id::text AS id,
                    u.username AS username,
                    u.email AS email,
                    d.last_name AS last_name,
                    d.first_name AS first_name,
                    d.middle_name AS middle_name,
                    TRIM(
                        COALESCE(d.last_name, '') || ' ' ||
                        COALESCE(d.first_name, '') || ' ' ||
                        COALESCE(d.middle_name, '')
                    ) AS full_name,
                    d.license_number AS license_number,
                    d.experience_years::int AS experience_years,
                    COALESCE(
                        ARRAY_REMOVE(ARRAY_AGG(DISTINCT s.name), NULL),
                        ARRAY[]::varchar[]
                    ) AS specializations,
                    d.monthly_salary::float8 AS monthly_salary,
                    d.bonus_percent::float8 AS bonus_percent,
                    d.is_active AS is_active
                FROM clinic.doctors d
                LEFT JOIN clinic.users u ON u.id = d.user_id
                LEFT JOIN clinic.doctor_specialties ds ON ds.doctor_id = d.id
                LEFT JOIN clinic.specialties s ON s.id = ds.specialty_id
                {filters}
                GROUP BY d.id, u.username, u.email, d.last_name, d.first_name, d.middle_name
                ORDER BY d.is_active DESC, full_name NULLS LAST, u.username NULLS LAST, d.id
                OFFSET :skip
                LIMIT :limit
                """
            ),
            params,
        ).mappings()
        return [self._normalize_row(dict(row)) for row in rows]

    def count_doctors(self, *, include_inactive: bool) -> int:
        filters = ""
        if not include_inactive:
            filters = "WHERE is_active = true"

        row = self.session.execute(
            text(
                f"""
                SELECT COUNT(*)::int AS total
                FROM clinic.doctors
                {filters}
                """
            )
        ).mappings().one()
        return int(row["total"])

    def list_specialties(self) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT id, name
                FROM clinic.specialties
                ORDER BY name
                """
            )
        ).mappings()
        return [dict(row) for row in rows]

    def specialty_exists(self, specialty_id: int) -> bool:
        row = self.session.execute(
            text("SELECT 1 FROM clinic.specialties WHERE id = :specialty_id LIMIT 1"),
            {"specialty_id": specialty_id},
        ).first()
        return row is not None

    def create_doctor(
        self,
        *,
        username: str,
        email: str,
        password_hash: str,
        last_name: str,
        first_name: str,
        middle_name: str | None,
        license_number: str,
        experience_years: int,
        specialty_ids: list[int],
        monthly_salary: float,
        bonus_percent: float,
        is_active: bool,
    ) -> dict:
        self.ensure_profile_columns()
        user_row = self.session.execute(
            text(
                """
                INSERT INTO clinic.users (id, username, email, password_hash, role, is_active)
                VALUES (gen_random_uuid(), :username, :email, :password_hash, 'doctor', :is_active)
                RETURNING id::text AS user_id
                """
            ),
            {
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "is_active": is_active,
            },
        ).mappings().one()

        row = self.session.execute(
            text(
                """
                INSERT INTO clinic.doctors (
                    id,
                    user_id,
                    license_number,
                    experience_years,
                    monthly_salary,
                    bonus_percent,
                    is_active
                )
                VALUES (
                    gen_random_uuid(),
                    CAST(:user_id AS uuid),
                    :license_number,
                    :experience_years,
                    :monthly_salary,
                    :bonus_percent,
                    :is_active
                )
                RETURNING id::text AS id
                """
            ),
            {
                "user_id": user_row["user_id"],
                "license_number": license_number,
                "experience_years": experience_years,
                "monthly_salary": monthly_salary,
                "bonus_percent": bonus_percent,
                "is_active": is_active,
            },
        ).mappings().one()
        self.session.execute(
            text(
                """
                UPDATE clinic.doctors
                SET
                    last_name = :last_name,
                    first_name = :first_name,
                    middle_name = :middle_name
                WHERE id = CAST(:doctor_id AS uuid)
                """
            ),
            {
                "doctor_id": row["id"],
                "last_name": last_name,
                "first_name": first_name,
                "middle_name": middle_name,
            },
        )

        for specialty_id in specialty_ids:
            self.session.execute(
                text(
                    """
                    INSERT INTO clinic.doctor_specialties (doctor_id, specialty_id)
                    VALUES (CAST(:doctor_id AS uuid), :specialty_id)
                    ON CONFLICT (doctor_id, specialty_id) DO NOTHING
                    """
                ),
                {"doctor_id": row["id"], "specialty_id": specialty_id},
            )

        created = self.session.execute(
            text(
                """
                SELECT
                    d.id::text AS id,
                    u.username AS username,
                    u.email AS email,
                    d.last_name AS last_name,
                    d.first_name AS first_name,
                    d.middle_name AS middle_name,
                    TRIM(
                        COALESCE(d.last_name, '') || ' ' ||
                        COALESCE(d.first_name, '') || ' ' ||
                        COALESCE(d.middle_name, '')
                    ) AS full_name,
                    d.license_number AS license_number,
                    d.experience_years::int AS experience_years,
                    COALESCE(
                        ARRAY_REMOVE(ARRAY_AGG(DISTINCT s.name), NULL),
                        ARRAY[]::varchar[]
                    ) AS specializations,
                    d.monthly_salary::float8 AS monthly_salary,
                    d.bonus_percent::float8 AS bonus_percent,
                    d.is_active AS is_active
                FROM clinic.doctors d
                LEFT JOIN clinic.users u ON u.id = d.user_id
                LEFT JOIN clinic.doctor_specialties ds ON ds.doctor_id = d.id
                LEFT JOIN clinic.specialties s ON s.id = ds.specialty_id
                WHERE d.id = CAST(:doctor_id AS uuid)
                GROUP BY d.id, u.username, u.email, d.last_name, d.first_name, d.middle_name
                """
            ),
            {"doctor_id": row["id"]},
        ).mappings().one()
        return self._normalize_row(dict(created))

    def update_doctor_employment(
        self,
        *,
        doctor_id: str,
        monthly_salary: float | None,
        bonus_percent: float | None,
        is_active: bool | None,
    ) -> dict | None:
        self.ensure_profile_columns()
        row = self.session.execute(
            text(
                """
                UPDATE clinic.doctors d
                SET
                    monthly_salary = COALESCE(:monthly_salary, d.monthly_salary),
                    bonus_percent = COALESCE(:bonus_percent, d.bonus_percent),
                    is_active = COALESCE(:is_active, d.is_active)
                WHERE d.id = CAST(:doctor_id AS uuid)
                RETURNING d.user_id::text AS user_id
                """
            ),
            {
                "doctor_id": doctor_id,
                "monthly_salary": monthly_salary,
                "bonus_percent": bonus_percent,
                "is_active": is_active,
            },
        ).mappings().first()
        if not row:
            return None

        if row["user_id"] is not None and is_active is not None:
            self.session.execute(
                text(
                    """
                    UPDATE clinic.users
                    SET is_active = :is_active
                    WHERE id = CAST(:user_id AS uuid)
                    """
                ),
                {"user_id": row["user_id"], "is_active": is_active},
            )

        updated = self.session.execute(
            text(
                """
                SELECT
                    d.id::text AS id,
                    u.username AS username,
                    u.email AS email,
                    d.last_name AS last_name,
                    d.first_name AS first_name,
                    d.middle_name AS middle_name,
                    TRIM(
                        COALESCE(d.last_name, '') || ' ' ||
                        COALESCE(d.first_name, '') || ' ' ||
                        COALESCE(d.middle_name, '')
                    ) AS full_name,
                    d.license_number AS license_number,
                    d.experience_years::int AS experience_years,
                    COALESCE(
                        ARRAY_REMOVE(ARRAY_AGG(DISTINCT s.name), NULL),
                        ARRAY[]::varchar[]
                    ) AS specializations,
                    d.monthly_salary::float8 AS monthly_salary,
                    d.bonus_percent::float8 AS bonus_percent,
                    d.is_active AS is_active
                FROM clinic.doctors d
                LEFT JOIN clinic.users u ON u.id = d.user_id
                LEFT JOIN clinic.doctor_specialties ds ON ds.doctor_id = d.id
                LEFT JOIN clinic.specialties s ON s.id = ds.specialty_id
                WHERE d.id = CAST(:doctor_id AS uuid)
                GROUP BY d.id, u.username, u.email, d.last_name, d.first_name, d.middle_name
                """
            ),
            {"doctor_id": doctor_id},
        ).mappings().one()
        return self._normalize_row(dict(updated))

    def get_doctor_id_by_user_id(self, user_id: str) -> str | None:
        row = self.session.execute(
            text(
                """
                SELECT d.id::text AS id
                FROM clinic.doctors d
                WHERE d.user_id = CAST(:user_id AS uuid)
                LIMIT 1
                """
            ),
            {"user_id": user_id},
        ).mappings().first()
        if not row:
            return None
        return str(row["id"])
