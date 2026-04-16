import { Button } from "./Button";

type ToastVariant = "success" | "error" | "info";

type ToastItem = {
  id: string;
  message: string;
  variant: ToastVariant;
};

type ToastViewportProps = {
  toasts: ToastItem[];
  onDismiss: (id: string) => void;
};

export function ToastViewport({ toasts, onDismiss }: ToastViewportProps) {
  if (toasts.length === 0) {
    return null;
  }

  return (
    <div className="ui-toast-viewport" aria-live="polite" aria-label="Уведомления">
      {toasts.map((toast) => (
        <div key={toast.id} className={`ui-toast ui-toast--${toast.variant}`}>
          <span>{toast.message}</span>
          <Button variant="ghost" onClick={() => onDismiss(toast.id)}>
            Закрыть
          </Button>
        </div>
      ))}
    </div>
  );
}
