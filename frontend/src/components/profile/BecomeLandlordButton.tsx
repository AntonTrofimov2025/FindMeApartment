import { useState } from 'react';
import { AlertTriangle, Building2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '@/hooks/useAuth';
import { Modal } from '@/components/ui/Modal';
import { parseApiError } from '@/lib/errors';
import { useI18n } from '@/i18n';

// UserBecomeLandlordView удаляет пользователя из группы Tenant и добавляет в Landlord.
// По карте ролей (ROLE_PERMISSION) у Landlord нет bookings.add_booking — это осознанное
// бизнес-правило: хозяин жилья не бронирует. Поэтому перед подтверждением явно предупреждаем,
// что шаг односторонний и бронирования станут недоступны (прошлые поездки останутся видны).
export function BecomeLandlordButton({ className = 'btn-secondary' }: { className?: string }) {
  const { becomeLandlord } = useAuth();
  const [showConfirm, setShowConfirm] = useState(false);
  const [acknowledged, setAcknowledged] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { t } = useI18n();

  async function handleConfirm() {
    setIsSubmitting(true);
    try {
      const res = await becomeLandlord();
      toast.success(res.msg ?? res.detail ?? t('landlord.success'));
      setShowConfirm(false);
    } catch (err) {
      toast.error(parseApiError(err).message);
    } finally {
      setIsSubmitting(false);
    }
  }

  function close() {
    setShowConfirm(false);
    setAcknowledged(false);
  }

  return (
    <>
      <button onClick={() => setShowConfirm(true)} className={className}>
        <Building2 size={16} className="mr-2" />
        {t('landlord.become')}
      </button>

      {showConfirm && (
        <Modal title={t('landlord.confirmTitle')} onClose={close}>
          <div className="space-y-4 text-sm text-neutral-700">
            <p>{t('landlord.benefits')}</p>

            <div className="flex gap-3 rounded-lg border border-amber-200 bg-amber-50 p-3.5 text-amber-900">
              <AlertTriangle size={18} className="mt-0.5 shrink-0" />
              <div className="space-y-1.5">
                <p className="font-semibold">{t('landlord.warningTitle')}</p>
                <p>{t('landlord.warningText')}</p>
              </div>
            </div>

            <label className="flex cursor-pointer items-start gap-2.5">
              <input
                type="checkbox"
                checked={acknowledged}
                onChange={(e) => setAcknowledged(e.target.checked)}
                className="mt-0.5 h-4 w-4 accent-brand-500"
              />
              <span>{t('landlord.acknowledge')}</span>
            </label>

            <div className="flex justify-end gap-2 pt-1">
              <button onClick={close} className="btn-secondary !px-4 !py-2 text-sm">
                {t('common.cancel')}
              </button>
              <button
                onClick={handleConfirm}
                disabled={!acknowledged || isSubmitting}
                className="btn-primary !px-4 !py-2 text-sm"
              >
                {isSubmitting ? t('landlord.processing') : t('landlord.become')}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </>
  );
}
