import type { PropsWithChildren } from "react";

type BadgeProps = PropsWithChildren<{
  variant?: "neutral" | "success" | "warning";
}>;

export function Badge({ children, variant = "neutral" }: BadgeProps) {
  return <span className={`ui-badge ui-badge--${variant}`}>{children}</span>;
}
