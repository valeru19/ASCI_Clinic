export type Appointment = {
  id: string;
  patient_id: string;
  patient_full_name?: string | null;
  doctor_id: string;
  doctor_full_name?: string | null;
  slot_id: string;
  status: string;
  created_at: string;
};

export type AppointmentListResponse = {
  items: Appointment[];
  total: number;
};

export type AppointmentCreatePayload = {
  patient_id: string;
  doctor_id: string;
  slot_id: string;
  reason?: string;
};

export type AppointmentCancelPayload = {
  reason?: string;
};

export type AppointmentReschedulePayload = {
  slot_id: string;
};
