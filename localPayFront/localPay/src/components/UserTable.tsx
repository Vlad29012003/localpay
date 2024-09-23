import React from 'react';
import { FiTrash2, FiEdit, FiPlusCircle, FiMinusCircle } from "react-icons/fi";

type User = {
  id: number;
  name: string;
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

interface UserTableProps {
  users: User[];
  onUpdateUser: (user: User) => void;
  onRefill: (userId: number) => void;
  onWriteOff: (userId: number) => void;
  userRole: string;
}

const UserTable: React.FC<UserTableProps> = ({ users, onUpdateUser, onRefill, onWriteOff, userRole }) => {
  return (
    <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-3xl p-8 shadow-2xl overflow-x-auto">
      <table className="w-full text-white border-collapse">
        <thead>
          <tr className="bg-white bg-opacity-20">
            <th className="px-4 py-2 text-left border-b border-r border-white border-opacity-20">ID</th>
            <th className="px-4 py-2 text-left border-b border-r border-white border-opacity-20">Имя</th>
            <th className="px-4 py-2 text-left border-b border-r border-white border-opacity-20">Фамилия</th>
            <th className="px-4 py-2 text-left border-b border-r border-white border-opacity-20">Логин</th>
            <th className="px-4 py-2 text-left border-b border-r border-white border-opacity-20">Админ</th>
            <th className="px-4 py-2 text-left border-b border-r border-white border-opacity-20">Доступ к платежам</th>
            <th className="px-4 py-2 text-left border-b border-r border-white border-opacity-20">Активный</th>
            <th className="px-4 py-2 text-left border-b border-r border-white border-opacity-20">Регион</th>
            <th className="px-4 py-2 text-left border-b border-r border-white border-opacity-20">Потрачено</th>
            <th className="px-4 py-2 text-left border-b border-r border-white border-opacity-20">Доступный баланс</th>
            {userRole === 'admin' && (
              <th className="px-4 py-2 text-left border-b border-white border-opacity-20">Действия</th>
            )}
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id} className="hover:bg-white hover:bg-opacity-10 transition duration-300">
              <td className="px-4 py-2 border-b border-r border-white border-opacity-10">{user.id}</td>
              <td className="px-4 py-2 border-b border-r border-white border-opacity-10">{user.name}</td>
              <td className="px-4 py-2 border-b border-r border-white border-opacity-10">{user.surname}</td>
              <td className="px-4 py-2 border-b border-r border-white border-opacity-10">{user.login}</td>
              <td className="px-4 py-2 border-b border-r border-white border-opacity-10">{user.is_admin ? "Да" : "Нет"}</td>
              <td className="px-4 py-2 border-b border-r border-white border-opacity-10">{user.access_to_payments ? "Да" : "Нет"}</td>
              <td className="px-4 py-2 border-b border-r border-white border-opacity-10">{user.is_active ? "Да" : "Нет"}</td>
              <td className="px-4 py-2 border-b border-r border-white border-opacity-10">{user.region}</td>
              <td className="px-4 py-2 border-b border-r border-white border-opacity-10">{user.available_balance}</td>
              <td className="px-4 py-2 border-b border-r border-white border-opacity-10">{user.spent_money}</td>
              {userRole === 'admin' && (
                <td className="px-4 py-2 border-b border-white border-opacity-10">
                  <div className="flex items-center space-x-2">
                    <button
                      className="p-1 text-white hover:text-blue-300 transition duration-300"
                      onClick={() => onUpdateUser(user)}
                    >
                      <FiEdit size={20} />
                    </button>
                    <button
                      className="p-1 text-white hover:text-green-300 transition duration-300"
                      onClick={() => onRefill(user.id)}
                    >
                      <FiPlusCircle size={20} />
                    </button>
                    <button
                      className="p-1 text-white hover:text-yellow-300 transition duration-300"
                      onClick={() => onWriteOff(user.id)}
                    >
                      <FiMinusCircle size={20} />
                    </button>
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default UserTable;