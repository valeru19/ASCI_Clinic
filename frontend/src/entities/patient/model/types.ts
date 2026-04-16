export type Gender = "M" | "F" | "O";

export type Patient = {
  id: string;
  last_name: string;
  first_name: string;
  middle_name: string | null;
  birth_date: string;
  gender: Gender;
  phone: string | null;
  email: string | null;
  insurance_number: string | null;
  address: string | null;
  is_active: boolean;
};

export type PatientListResponse = {
  items: Patient[];
  total: number;
};

export type PatientCreatePayload = {
  last_name: string;
  first_name: string;
  birth_date: string;
  gender: Gender;
  phone?: string;
  email?: string;
};
