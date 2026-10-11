import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { AlertTriangle } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { Modal } from '@/components/ui/Modal';
import { parseApiError } from '@/lib/errors';
import { useI18n } from '@/i18n';

export function DangerZone() {
  const { deleteAccount, isLandlord } = useAuth();
  const navigate = useNavigate();
  const [showConfirm, setShowConfirm] = useState(false);
  const [confirmText, setConfirmText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const { t, intlLocale } = useI18n();
  // Слово-подтверждение своё для каждого языка (УДАЛИТЬ / LÖSCHEN / DELETE); регистр не важен.
  const confirmWord = t('danger.confirmWord');
  const isConfirmed = confirmText.trim().toLocaleUpperCase(intlLocale) === confirmWord.toLocaleUpperCase(intlLocale);

  async function handleDelete() {
    setIsDeleting(true);
    try {
      const res = await deleteAccount();
      toast.success(res.msg);
      navigate('/');
    } catch (err) {
      toast.error(parseApiError(err).message);
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <div className="card space-y-3 border-red-200 p-6">
      <div className="flex items-center gap-2 text-red-600">
        <AlertTriangle size={18} />
        <h2 className="text-lg font-semibold">{t('danger.title')}</h2>
      </div>
      <p className="text-sm text-neutral-600">{t('danger.text')}</p>
      {isLandlord && (
        <p className="rounded-lg border border-red-100 bg-red-50 p-3 text-sm text-red-700">
          {t('danger.landlordWarning')}
        </p>
      )}
      <button onClick={() => setShowConfirm(true)} className="btn-secondary border-red-300 text-red-600 hover:bg-red-50">
        {t('danger.deleteAccount')}
      </button>

      {showConfirm && (
        <Modal
          title={t('danger.confirmTitle')}
          onClose={() => {
            setShowConfirm(false);
            setConfirmText('');
          }}
        >
          <p className="mb-3 text-sm text-neutral-600">
            {/* Плейсхолдер {word} разрезаем вручную, чтобы выделить само слово жирным */}
            {t('danger.confirmText').split('{word}').map((part, i, parts) => (
              <span key={i}>
                {part}
                {i < parts.length - 1 && <strong>{confirmWord}</strong>}
              </span>
            ))}
          </p>
          <input
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            className="input mb-4"
            placeholder={confirmWord}
          />
          <div className="flex justify-end gap-2">
            <button onClick={() => setShowConfirm(false)} className="btn-secondary !px-4 !py-2 text-sm">
              {t('common.cancel')}
            </button>
            <button
              onClick={handleDelete}
              disabled={!isConfirmed || isDeleting}
              className="btn-primary !bg-red-600 !px-4 !py-2 text-sm hover:!bg-red-700"
            >
              {isDeleting ? t('danger.deleting') : t('danger.deleteForever')}
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}
