import { httpRequest } from "@/shared/api/httpClient";

import type { ScheduleSlotListResponse } from "../model/types";

export const scheduleSlotApi = {
  listAvailableByDoctor: (
    token: string,
    doctorId: string,
    dateFrom: string,
    dateTo: string,
    skip = 0,
    limit = 100,
  ) => {
    const params = new URLSearchParams({
      doctor_id: doctorId,
      date_from: dateFrom,
      date_to: dateTo,
      status: "available",
      skip: String(skip),
      limit: String(limit),
    });
    return httpRequest<ScheduleSlotListResponse>(`/schedule-slots/?${params.toString()}`, {
      token,
    });
  },
};
