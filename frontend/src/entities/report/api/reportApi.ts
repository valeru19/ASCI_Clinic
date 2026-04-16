import { httpRequest } from "@/shared/api/httpClient";

import type { DiagnosesStatsResponse } from "../model/types";

export const reportApi = {
  diagnoses: (token: string, dateFrom: string, dateTo: string, limit: number) => {
    const params = new URLSearchParams({
      date_from: dateFrom,
      date_to: dateTo,
      limit: String(limit),
    });
    return httpRequest<DiagnosesStatsResponse>(`/reports/diagnoses?${params.toString()}`, {
      token,
    });
  },
};
