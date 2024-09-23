import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaHome, FaUsers, FaChartBar, FaSignOutAlt, FaPlus, FaUserPlus } from 'react-icons/fa';
import { jwtDecode } from 'jwt-decode';
import { DecodedToken } from '../../components/DecodedToken';
import useRoleRedirect, { handleLogout } from '../../hooks/useRoleRedirect';

const AdminPanel: React.FC = () => {

  useRoleRedirect(['admin']);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex flex-col items-center justify-center text-white p-4">
      <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-3xl p-8 shadow-2xl w-full max-w-4xl">
        <h1 className="text-4xl font-bold mb-8 text-center">
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-purple-100 drop-shadow-md">
            Панель администратора
          </span>
        </h1>
        <nav className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Link 
            to="/admin" 
            className="flex items-center justify-center bg-white text-purple-600 px-6 py-4 rounded-xl font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-purple-100"
          >
            <FaHome className="mr-3 text-2xl" />
            Главная
          </Link>
          <Link 
            to="/users" 
            className="flex items-center justify-center bg-white text-blue-600 px-6 py-4 rounded-xl font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-blue-100"
          >
            <FaUsers className="mr-3 text-2xl" />
            Пользователи
          </Link>
          <Link 
            to="/reports" 
            className="flex items-center justify-center bg-white text-green-600 px-6 py-4 rounded-xl font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-green-100"
          >
            <FaChartBar className="mr-3 text-2xl" />
            Отчеты
          </Link>
          <Link 
            to="/payments" 
            className="flex items-center justify-center bg-white text-yellow-600 px-6 py-4 rounded-xl font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-yellow-100"
          >
            <FaChartBar className="mr-3 text-2xl" />
            Платежи
          </Link>
          <Link 
            to="/register" 
            className="flex items-center justify-center bg-white text-black px-6 py-4 rounded-xl font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-gray-200"
          >
            <FaUserPlus className="mr-3 text-2xl" />
            Добавить пользователя
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

export default AdminPanel;
