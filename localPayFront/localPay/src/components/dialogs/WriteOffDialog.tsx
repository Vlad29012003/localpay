import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
} from "@material-ui/core";

interface WriteOffDialogProps {
  open: boolean;
  onClose: () => void;
  onWriteOff: (amount: number) => void;
}

const WriteOffDialog: React.FC<WriteOffDialogProps> = ({ open, onClose, onWriteOff }) => {
  const [writeOffAmount, setWriteOffAmount] = useState<number>(0);

  const handleWriteOff = () => {
    onWriteOff(writeOffAmount);
    setWriteOffAmount(0);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle className="bg-yellow-600 text-white">Списать с баланса</DialogTitle>
      <DialogContent className="space-y-4 pt-4">
        <TextField
          label="Сумма"
          fullWidth
          type="number"
          value={writeOffAmount}
          onChange={(e) => setWriteOffAmount(parseFloat(e.target.value))}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="secondary">
          Отменить
        </Button>
        <Button onClick={handleWriteOff} color="primary">
          Списать
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default WriteOffDialog;