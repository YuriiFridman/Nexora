import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { channelsApi } from '@/lib/api';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface Props {
  open: boolean;
  guildId: string;
  onClose: () => void;
}

export default function CreateCategoryModal({ open, guildId, onClose }: Props) {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  const create = useMutation({
    mutationFn: () => channelsApi.createCategory(guildId, { name: name.trim() }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['categories', guildId] });
      setName('');
      setError('');
      onClose();
    },
    onError: (e: Error) => setError(e.message),
  });

  function handleClose() {
    setName('');
    setError('');
    onClose();
  }

  return (
    <Dialog open={open} onOpenChange={(v) => !v && handleClose()}>
      <DialogContent style={{ background: 'var(--bg-secondary)', border: '1px solid rgba(255,255,255,0.08)', color: 'var(--text-primary)' }}>
        <DialogHeader>
          <DialogTitle style={{ color: 'var(--text-primary)' }}>{t('channel.createCategory')}</DialogTitle>
        </DialogHeader>

        <div className="space-y-3 pt-2">
          <div>
            <label className="text-xs font-semibold uppercase mb-1 block" style={{ color: 'var(--text-muted)' }}>
              {t('channel.categoryName')}
            </label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t('channel.categoryNamePlaceholder')}
              maxLength={100}
              onKeyDown={(e) => e.key === 'Enter' && name.trim() && create.mutate()}
              style={{ background: 'var(--bg-primary)', border: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-primary)' }}
            />
          </div>

          {error && <p className="text-sm" style={{ color: 'var(--danger)' }}>{error}</p>}

          <div className="flex justify-end gap-2 pt-2">
            <Button variant="ghost" onClick={handleClose} style={{ color: 'var(--text-secondary)' }}>
              {t('common.cancel')}
            </Button>
            <Button
              onClick={() => create.mutate()}
              disabled={!name.trim() || create.isPending}
              style={{ background: 'var(--accent)', color: '#fff' }}
            >
              {create.isPending ? t('common.loading') : t('common.create')}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
