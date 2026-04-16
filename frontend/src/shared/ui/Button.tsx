import type { ButtonHTMLAttributes, PropsWithChildren } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

type ButtonProps = PropsWithChildren<
  ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: ButtonVariant;
    block?: boolean;
  }
>;

export function Button({
  children,
  className,
  variant = "primary",
  block = false,
  ...rest
}: ButtonProps) {
  const classes = [
    "ui-btn",
    `ui-btn--${variant}`,
    block ? "ui-btn--block" : "",
    className ?? "",
  ]
    .join(" ")
    .trim();

  return (
    <button className={classes} {...rest}>
      {children}
    </button>
  );
}
