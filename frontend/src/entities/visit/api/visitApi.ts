import { httpRequest } from "@/shared/api/httpClient";

import type {
  DiagnosesCreatePayload,
  DiagnosesCreateResponse,
  VisitListResponse,
} from "../model/types";

export const visitApi = {
  list: (
    token: string,
    skip: number,
    limit: number,
    filters?: { doctorId?: string; patientId?: string; status?: string },
  ) => {
    const params = new URLSearchParams();
    params.set("skip", String(skip));
    params.set("limit", String(limit));
    if (filters?.doctorId) {
      params.set("doctor_id", filters.doctorId);
    }
    if (filters?.patientId) {
      params.set("patient_id", filters.patientId);
    }
    if (filters?.status) {
      params.set("status", filters.status);
    }
    return httpRequest<VisitListResponse>(`/visits/?${params.toString()}`, { token });
  },
  addDiagnoses: (token: string, visitId: string, payload: DiagnosesCreatePayload) =>
    httpRequest<DiagnosesCreateResponse>(`/visits/${visitId}/diagnoses`, {
      method: "POST",
      token,
      body: payload,
    }),
};
