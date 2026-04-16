export type Visit = {
  id: string;
  appointment_id: string;
  patient_id: string;
  patient_full_name: string;
  doctor_id: string;
  doctor_full_name: string;
  chief_complaint: string;
  exam_notes: string;
  treatment_plan: string | null;
  visit_status: "in_progress" | "completed" | "cancelled";
  closed_at: string | null;
};

export type VisitListResponse = {
  items: Visit[];
  total: number;
};

export type DiagnosesCreatePayload = {
  items: Array<{
    icd10_code: string;
    is_primary: boolean;
    comment?: string;
  }>;
};

export type DiagnosesCreateResponse = {
  visit_id: string;
  created: number;
  diagnoses: Array<{
    id: string;
    icd10_code: string;
    is_primary: boolean;
    comment: string | null;
  }>;
};
