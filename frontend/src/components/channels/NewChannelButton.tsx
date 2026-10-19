import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { hapticImpact } from '@/lib/telegram';

interface NewChannelButtonProps {
  compact?: boolean;
}

export function NewChannelButton({ compact = false }: NewChannelButtonProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    hapticImpact('medium');
    navigate('/channels/new');
  };

  return (
    <Button
      variant="primary"
      size={compact ? 'sm' : 'md'}
      leftIcon={<Plus size={16} />}
      onClick={handleClick}
      id="new-channel-btn"
    >
      {compact ? 'Add Channel' : 'Connect Channel'}
    </Button>
  );
}
