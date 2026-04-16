import { httpRequest } from "@/shared/api/httpClient";

import type { Patient, PatientCreatePayload, PatientListResponse } from "../model/types";

export const patientApi = {
  list: (token: string, q: string, skip: number, limit: number) => {
    const params = new URLSearchParams({
      skip: String(skip),
      limit: String(limit),
    });
    if (q.trim()) {
      params.set("q", q.trim());
    }
    return httpRequest<PatientListResponse>(`/patients/?${params.toString()}`, { token });
  },
  create: (token: string, payload: PatientCreatePayload) =>
    httpRequest<Patient>("/patients/", {
      method: "POST",
      token,
      body: payload,
    }),
};
