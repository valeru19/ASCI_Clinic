export type Doctor = {
  id: string;
  username: string | null;
  email: string | null;
  last_name: string | null;
  first_name: string | null;
  middle_name: string | null;
  full_name: string;
  license_number: string;
  experience_years: number;
  specializations: string[];
  monthly_salary: number;
  bonus_percent: number;
  is_active: boolean;
};

export type DoctorListResponse = {
  items: Doctor[];
  total: number;
};

export type DoctorCreatePayload = {
  username: string;
  email: string;
  password: string;
  last_name: string;
  first_name: string;
  middle_name?: string;
  license_number: string;
  experience_years: number;
  specialty_ids: number[];
  monthly_salary: number;
  bonus_percent: number;
  is_active: boolean;
};

export type DoctorEmploymentUpdatePayload = {
  monthly_salary?: number;
  bonus_percent?: number;
  is_active?: boolean;
};
