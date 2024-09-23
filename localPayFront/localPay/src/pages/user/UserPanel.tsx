import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaUser, FaMoneyBillWave, FaSignOutAlt, FaHome } from 'react-icons/fa';
import { useAuth } from '../../auth/AuthContext';
import { DecodedToken } from '../../components/DecodedToken';
import { jwtDecode } from 'jwt-decode';
import useRoleRedirect, { handleLogout } from '../../hooks/useRoleRedirect';

const UserPanel: React.FC = () => {
  useRoleRedirect(['user']);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-400 to-blue-600 flex flex-col items-center justify-center text-white p-4">
      <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-3xl p-8 shadow-2xl w-full max-w-4xl">
        <h1 className="text-4xl font-bold mb-8 text-center">
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-blue-100 drop-shadow-md">
            Панель пользователя
          </span>
        </h1>
        <nav className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Link 
            to="/" 
            className="flex items-center justify-center bg-white text-purple-600 px-6 py-4 rounded-xl font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-purple-100"
          >
            <FaHome className="mr-3 text-2xl" />
            Главная
          </Link>
          <Link 
            to="/profile" 
            className="flex items-center justify-center bg-white text-blue-600 px-6 py-4 rounded-xl font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-blue-100"
          >
            <FaUser className="mr-3 text-2xl" />
            Профиль
          </Link>
          <Link 
            to="/makepayment" 
            className="flex items-center justify-center bg-white text-green-600 px-6 py-4 rounded-xl font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-green-100"
          >
            <FaMoneyBillWave className="mr-3 text-2xl" />
            Оплатить
          </Link>
          <button 
            className="flex items-center justify-center bg-white text-red-600 px-6 py-4 rounded-xl font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-red-100"
            onClick={handleLogout}
          >
            <FaSignOutAlt className="mr-3 text-2xl" />
            Выход
          </button>
        </nav>
      </div>
      <footer className="mt-12 text-sm text-white text-opacity-80">
        © 2024 LocalPay. Все права защищены.
      </footer>
    </div>
  );
};

export default UserPanel;