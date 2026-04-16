import type { PropsWithChildren } from "react";

type AlertProps = PropsWithChildren<{
  variant: "success" | "error" | "info";
}>;

export function Alert({ variant, children }: AlertProps) {
  return <div className={`ui-alert ui-alert--${variant}`}>{children}</div>;
}
