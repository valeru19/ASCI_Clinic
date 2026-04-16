import type { PropsWithChildren, ReactNode } from "react";

type CardProps = PropsWithChildren<{
  title?: string;
  subtitle?: string;
  action?: ReactNode;
}>;

export function Card({ title, subtitle, action, children }: CardProps) {
  return (
    <section className="ui-card">
      {(title || subtitle || action) && (
        <header className="ui-card__header">
          <div>
            {title && <h2 className="ui-card__title">{title}</h2>}
            {subtitle && <p className="ui-card__subtitle">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </header>
      )}
      <div className="ui-card__content">{children}</div>
    </section>
  );
}
