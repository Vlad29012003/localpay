import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
} from "@material-ui/core";

interface RefillDialogProps {
  open: boolean;
  onClose: () => void;
  onRefill: (amount: number) => void;
}

const RefillDialog: React.FC<RefillDialogProps> = ({ open, onClose, onRefill }) => {
  const [refillAmount, setRefillAmount] = useState<number>(0);

  const handleRefill = () => {
    onRefill(refillAmount);
    setRefillAmount(0);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle className="bg-green-600 text-white">Пополнить баланс</DialogTitle>
      <DialogContent className="space-y-4 pt-4">
        <TextField
          label="Сумма"
          fullWidth
          type="number"
          value={refillAmount}
          onChange={(e) => setRefillAmount(parseFloat(e.target.value))}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="secondary">
          Отменить
        </Button>
        <Button onClick={handleRefill} color="primary">
          Пополнить
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RefillDialog;