import { useState } from 'react';
import { AlertTriangle, Building2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '@/hooks/useAuth';
import { Modal } from '@/components/ui/Modal';
import { parseApiError } from '@/lib/errors';

// UserBecomeLandlordView удаляет пользователя из группы Tenant и добавляет в Landlord.
// По карте ролей (ROLE_PERMISSION) у Landlord нет bookings.add_booking — это осознанное
// бизнес-правило: хозяин жилья не бронирует. Поэтому перед подтверждением явно предупреждаем,
// что шаг односторонний и бронирования станут недоступны (прошлые поездки останутся видны).
export function BecomeLandlordButton({ className = 'btn-secondary' }: { className?: string }) {
  const { becomeLandlord } = useAuth();
  const [showConfirm, setShowConfirm] = useState(false);
  const [acknowledged, setAcknowledged] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleConfirm() {
    setIsSubmitting(true);
    try {
      const res = await becomeLandlord();
      toast.success(res.msg ?? res.detail ?? 'Теперь вы арендодатель');
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
        Стать арендодателем
      </button>

      {showConfirm && (
        <Modal title="Стать арендодателем?" onClose={close}>
          <div className="space-y-4 text-sm text-neutral-700">
            <p>
              Вы сможете размещать объявления, загружать фото, принимать и подтверждать бронирования, а
              также видеть аналитику по своим объектам.
            </p>

            <div className="flex gap-3 rounded-lg border border-amber-200 bg-amber-50 p-3.5 text-amber-900">
              <AlertTriangle size={18} className="mt-0.5 shrink-0" />
              <div className="space-y-1.5">
                <p className="font-semibold">Бронировать жильё вы больше не сможете</p>
                <p>
                  Роль арендатора будет снята с аккаунта. Все ваши прошлые и текущие поездки останутся в
                  истории, а подтверждённые бронирования сохранятся, но новые бронирования создавать будет
                  нельзя. Вернуть роль арендатора самостоятельно не получится.
                </p>
              </div>
            </div>

            <label className="flex cursor-pointer items-start gap-2.5">
              <input
                type="checkbox"
                checked={acknowledged}
                onChange={(e) => setAcknowledged(e.target.checked)}
                className="mt-0.5 h-4 w-4 accent-brand-500"
              />
              <span>Понимаю, что после смены роли не смогу бронировать жильё</span>
            </label>

            <div className="flex justify-end gap-2 pt-1">
              <button onClick={close} className="btn-secondary !px-4 !py-2 text-sm">
                Отмена
              </button>
              <button
                onClick={handleConfirm}
                disabled={!acknowledged || isSubmitting}
                className="btn-primary !px-4 !py-2 text-sm"
              >
                {isSubmitting ? 'Обработка...' : 'Стать арендодателем'}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </>
  );
}
