import React from 'react';

interface UserFiltersProps {
  onSearchChange: (value: string) => void;
  onMinBalanceChange: (value: number | undefined) => void;
  onMaxBalanceChange: (value: number | undefined) => void;
}

const UserFilters: React.FC<UserFiltersProps> = ({ onSearchChange, onMinBalanceChange, onMaxBalanceChange }) => {
  return (
    <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-3xl p-6 shadow-2xl mb-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <input
            className="w-full bg-white bg-opacity-20 text-white placeholder-white placeholder-opacity-70 rounded-full px-6 py-3 outline-none transition duration-300 ease-in-out focus:ring-2 focus:ring-purple-300"
            type="text"
            placeholder="Поиск"
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>
        <div>
          <input
            className="w-full bg-white bg-opacity-20 text-white placeholder-white placeholder-opacity-70 rounded-full px-6 py-3 outline-none transition duration-300 ease-in-out focus:ring-2 focus:ring-purple-300"
            type="number"
            min="0"
            placeholder="Минимальный баланс"
            onChange={(e) => onMinBalanceChange(e.target.value ? parseInt(e.target.value) : undefined)}
          />
        </div>
        <div>
          <input
            className="w-full bg-white bg-opacity-20 text-white placeholder-white placeholder-opacity-70 rounded-full px-6 py-3 outline-none transition duration-300 ease-in-out focus:ring-2 focus:ring-purple-300"
            type="number"
            min="0"
            placeholder="Максимальный баланс"
            onChange={(e) => onMaxBalanceChange(e.target.value ? parseInt(e.target.value) : undefined)}
          />
        </div>
      </div>
    </div>
  );
};

export default UserFilters;