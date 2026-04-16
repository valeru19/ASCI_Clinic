export type Specialty = {
  id: number;
  name: string;
};

export type SpecialtyListResponse = {
  items: Specialty[];
  total: number;
};
