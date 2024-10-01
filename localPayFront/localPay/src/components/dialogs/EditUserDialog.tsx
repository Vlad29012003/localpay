import React, {useState, useEffect} from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Switch,
  FormControlLabel,
} from "@material-ui/core";

type User = {
  id: number;
  name: string;
  password?: string;
  confirmPassword?: string;
  login: string;
  is_admin: boolean;
  is_active: boolean;
  spent_money: number;
  surname: string;
  date_reg: string;
  access_to_payments: boolean;
  available_balance: number;
  region: string;
  comment: string;
};

interface EditUserDialogProps {
  open: boolean;
  user: User | null;
  onClose: () => void;
  onUpdate: (user: User) => void;
}

const EditUserDialog: React.FC<EditUserDialogProps> = ({open, user, onClose, onUpdate}) => {
  const [editedUser, setEditedUser] = useState<User | null>(null);
  
  useEffect(() => {
    setEditedUser(user);
    return () => setEditedUser(null);
  }, [user]);
  
  const handleInputChange = (field: keyof User, value: any) => {
    if (editedUser) {
      setEditedUser({...editedUser, [field]: value});
    }
  };
  
  const handleUpdateSubmit = () => {
    if (editedUser) {
      onUpdate(editedUser);
      onClose();
      setEditedUser(_ => ({
        ...editedUser,
        password: '',
        confirmPassword: '',
      }));
    }
  };
  
  if (!editedUser) return null;
  
  return (
    <Dialog
      open={open}
      onClose={() => {
        onClose();
        setEditedUser(_ => ({
          ...editedUser,
          password: '',
          confirmPassword: '',
        }));
      }}
      maxWidth='sm'
      fullWidth
    >
      <DialogTitle className='bg-blue-600 text-white'>Обновить юзера</DialogTitle>
      <DialogContent className='space-y-4 pt-4'>
        <div className='grid grid-cols-2 gap-4'>
          <TextField
            label='Имя'
            fullWidth
            value={editedUser.name}
            onChange={(e) => handleInputChange("name", e.target.value)}
          />
          <TextField
            label='Фамилия'
            fullWidth
            value={editedUser.surname}
            onChange={(e) => handleInputChange("surname", e.target.value)}
          />
        </div>
        <TextField
          label='Логин'
          fullWidth
          value={editedUser.login}
          onChange={(e) => handleInputChange("login", e.target.value)}
        />
        <TextField
          label='Пароль'
          type='password'
          fullWidth
          value={editedUser.password}
          onChange={(e) => handleInputChange("password", e.target.value)}
          helperText={!!editedUser?.password && editedUser.password.length < 6 ? 'Минимум 6 символов' : ''}
        />
        <TextField
          label='Подтвердите пароль'
          type='password'
          fullWidth
          value={editedUser.confirmPassword}
          onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
          error={!!editedUser?.password && !!editedUser?.confirmPassword && editedUser?.password !== editedUser?.confirmPassword}
          helperText={!!editedUser?.password && !!editedUser?.confirmPassword && editedUser?.password !== editedUser?.confirmPassword ? 'Пароли не совпадают' : ' '}
        />
        <div className='grid grid-cols-2 gap-4'>
          <FormControlLabel
            control={
              <Switch
                checked={editedUser.is_admin}
                onChange={(e) => handleInputChange("is_admin", e.target.checked)}
                color='primary'
              />
            }
            label='Админ'
          />
          <FormControlLabel
            control={
              <Switch
                checked={editedUser.access_to_payments}
                onChange={(e) => handleInputChange("access_to_payments", e.target.checked)}
                color='primary'
              />
            }
            label='Доступ к оплатам'
          />
        </div>
        <FormControlLabel
          control={
            <Switch
              checked={editedUser.is_active}
              onChange={(e) => handleInputChange("is_active", e.target.checked)}
              color='primary'
            />
          }
          label='Активен'
        />
        <TextField
          label='Доступный баланс'
          fullWidth
          type='number'
          value={editedUser.available_balance}
          onChange={(e) => handleInputChange("available_balance", parseFloat(e.target.value))}
        />
        <TextField
          label='Регион'
          fullWidth
          value={editedUser.region}
          onChange={(e) => handleInputChange("region", e.target.value)}
        />
        <TextField
          label='Комментарий'
          fullWidth
          multiline
          rows={3}
          value={editedUser.comment}
          onChange={(e) => handleInputChange("comment", e.target.value)}
        />
      </DialogContent>
      <DialogActions>
        <Button
          onClick={() => {
            onClose();
            setEditedUser(_ => ({
              ...editedUser,
              password: '',
              confirmPassword: '',
            }));
          }}
          color='secondary'
        >
          Отменить
        </Button>
        <Button
          onClick={handleUpdateSubmit}
          color='primary'
          disabled={
            (editedUser?.password && editedUser.password?.length < 6) ||
            (editedUser?.confirmPassword && editedUser.confirmPassword?.length < 6) ||
            Boolean((editedUser?.password && editedUser.password?.length >= 6 && ((editedUser?.confirmPassword && editedUser?.confirmPassword.length < 6) || !editedUser?.confirmPassword))) ||
            Boolean((editedUser?.confirmPassword && editedUser.confirmPassword?.length >= 6 && ((editedUser?.password && editedUser?.password.length < 6) || !editedUser?.password))) ||
            Boolean(editedUser?.password && editedUser.confirmPassword && editedUser.confirmPassword?.length >= 6 && editedUser.confirmPassword?.length >= 6 && editedUser?.password !== editedUser.confirmPassword)
          }
        >
          Обновить
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EditUserDialog;