export type ScheduleSlot = {
  id: string;
  schedule_id: string;
  start_at: string;
  end_at: string;
  status: "available" | "booked" | "blocked" | "cancelled";
};

export type ScheduleSlotListResponse = {
  items: ScheduleSlot[];
  total: number;
};
