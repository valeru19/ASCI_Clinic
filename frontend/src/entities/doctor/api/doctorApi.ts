import { httpRequest } from "@/shared/api/httpClient";

import type {
  Doctor,
  DoctorCreatePayload,
  DoctorEmploymentUpdatePayload,
  DoctorListResponse,
} from "../model/types";

export const doctorApi = {
  list: (token: string, skip = 0, limit = 100) => {
    const params = new URLSearchParams({
      skip: String(skip),
      limit: String(limit),
    });
    return httpRequest<DoctorListResponse>(`/doctors/?${params.toString()}`, { token });
  },
  create: (token: string, payload: DoctorCreatePayload) =>
    httpRequest<Doctor>("/doctors/", {
      method: "POST",
      token,
      body: payload,
    }),
  updateEmployment: (token: string, doctorId: string, payload: DoctorEmploymentUpdatePayload) =>
    httpRequest<Doctor>(`/doctors/${doctorId}/employment`, {
      method: "PATCH",
      token,
      body: payload,
    }),
};
