import { httpRequest } from "@/shared/api/httpClient";

import type {
  Appointment,
  AppointmentCancelPayload,
  AppointmentCreatePayload,
  AppointmentListResponse,
  AppointmentReschedulePayload,
} from "../model/types";

export const appointmentApi = {
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
    return httpRequest<AppointmentListResponse>(`/appointments/?${params.toString()}`, {
      token,
    });
  },
  create: (token: string, payload: AppointmentCreatePayload) =>
    httpRequest<Appointment>("/appointments/", {
      method: "POST",
      token,
      body: payload,
    }),
  cancel: (token: string, appointmentId: string, payload: AppointmentCancelPayload = {}) =>
    httpRequest<Appointment>(`/appointments/${appointmentId}/cancel`, {
      method: "PATCH",
      token,
      body: payload,
    }),
  reschedule: (token: string, appointmentId: string, payload: AppointmentReschedulePayload) =>
    httpRequest<Appointment>(`/appointments/${appointmentId}/reschedule`, {
      method: "PATCH",
      token,
      body: payload,
    }),
};
