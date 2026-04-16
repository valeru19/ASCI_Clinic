import { httpRequest } from "@/shared/api/httpClient";

import type { SpecialtyListResponse } from "../model/types";

export const specialtyApi = {
  list: (token: string) => httpRequest<SpecialtyListResponse>("/specialties/", { token }),
};
