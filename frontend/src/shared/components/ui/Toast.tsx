import { useToastStore } from '../../store/toastStore';

const icons: Record<string, string> = {
  success: 'M5 13l4 4L19 7',
  error: 'M6 6l12 12M6 18L18 6',
  info: 'M12 16v-4m0-4h.01',
};

const bgMap: Record<string, string> = {
  success: 'var(--toast-success-bg)',
  error: 'var(--toast-error-bg)',
  info: 'var(--toast-info-bg)',
};

const colorMap: Record<string, string> = {
  success: 'var(--toast-success-text)',
  error: 'var(--toast-error-text)',
  info: 'var(--toast-info-text)',
};

export function ToastContainer() {
  const toasts = useToastStore((s) => s.toasts);
  const removeToast = useToastStore((s) => s.removeToast);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-[var(--space-4)] right-[var(--space-4)] z-[100] flex flex-col gap-[var(--space-2)] max-w-sm">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          role="alert"
          className="flex items-start gap-[var(--space-3)] px-[var(--space-4)] py-[var(--space-3)] rounded-[var(--radius-md)] shadow-[var(--shadow-md)] border border-[var(--color-border)]"
          style={{
            animation: toast.exiting
              ? 'toastExit 0.3s ease-in forwards'
              : 'toastEnter 0.3s ease-out',
            backgroundColor: bgMap[toast.type],
            color: colorMap[toast.type],
          }}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="shrink-0 mt-[1px]">
            <path d={icons[toast.type] || icons.info} />
          </svg>
          <span className="text-[var(--font-size-sm)] font-medium flex-1">{toast.message}</span>
          <button
            onClick={() => removeToast(toast.id)}
            className="bg-transparent border-none p-0 text-current opacity-60 hover:opacity-100 shrink-0"
            aria-label="Fechar"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M6 6l12 12M6 18L18 6" />
            </svg>
          </button>
        </div>
      ))}
    </div>
  );
}
