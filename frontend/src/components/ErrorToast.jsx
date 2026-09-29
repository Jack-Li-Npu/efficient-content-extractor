import { CircleAlert, X } from 'lucide-react';

export default function ErrorToast({ error, onClose }) {
  if (!error) return null;
  return (
    <div role="alert" className="inline-error">
      <CircleAlert size={17} /><p>{error}</p>
      <button type="button" onClick={onClose} aria-label="Dismiss error" className="icon-button"><X size={15} /></button>
    </div>
  );
}
