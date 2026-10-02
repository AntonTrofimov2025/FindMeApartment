import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { AlertTriangle } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { Modal } from '@/components/ui/Modal';
import { parseApiError } from '@/lib/errors';

export function DangerZone() {
  const { deleteAccount, isLandlord } = useAuth();
  const navigate = useNavigate();
  const [showConfirm, setShowConfirm] = useState(false);
  const [confirmText, setConfirmText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

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
        <h2 className="text-lg font-semibold">Закрытие аккаунта</h2>
      </div>
      <p className="text-sm text-neutral-600">
        Аккаунт будет мягко удалён (<code>is_active=False</code>, фиксируется <code>deleted_at</code>) — вход по
        этим данным станет невозможен, но история бронирований и финансовые снимки сохранятся для отчётности.
        Восстановить доступ самостоятельно после этого нельзя.
      </p>
      {isLandlord && (
        <p className="rounded-lg border border-red-100 bg-red-50 p-3 text-sm text-red-700">
          Вместе с аккаунтом будут скрыты и удалены все ваши объявления. Если у гостей есть подтверждённые
          будущие бронирования, сначала отмените их — иначе гости останутся с бронями на недоступные объекты.
        </p>
      )}
      <button onClick={() => setShowConfirm(true)} className="btn-secondary border-red-300 text-red-600 hover:bg-red-50">
        Удалить аккаунт
      </button>

      {showConfirm && (
        <Modal title="Вы уверены?" onClose={() => setShowConfirm(false)}>
          <p className="mb-3 text-sm text-neutral-600">
            Это действие необратимо из интерфейса. Введите <strong>УДАЛИТЬ</strong>, чтобы подтвердить.
          </p>
          <input
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            className="input mb-4"
            placeholder="УДАЛИТЬ"
          />
          <div className="flex justify-end gap-2">
            <button onClick={() => setShowConfirm(false)} className="btn-secondary !px-4 !py-2 text-sm">
              Отмена
            </button>
            <button
              onClick={handleDelete}
              disabled={confirmText !== 'УДАЛИТЬ' || isDeleting}
              className="btn-primary !bg-red-600 !px-4 !py-2 text-sm hover:!bg-red-700"
            >
              {isDeleting ? 'Удаление...' : 'Удалить окончательно'}
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}
