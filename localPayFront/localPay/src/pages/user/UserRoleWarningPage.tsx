import React from 'react';
import { Link } from 'react-router-dom';
import { FaExclamationTriangle, FaHome } from 'react-icons/fa';

const UserRoleWarningPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex flex-col items-center justify-center text-white p-4">
      <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-3xl p-8 shadow-2xl max-w-2xl">
        <div className="flex items-center justify-center mb-6">
          <FaExclamationTriangle className="text-yellow-300 text-5xl" />
        </div>
        <h1 className="text-4xl font-bold mb-6 text-center">
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-purple-100">
            Ограниченный доступ
          </span>
        </h1>
        <p className="text-xl text-center mb-8">
          К сожалению, у вас права пользователя, а эта система предназначена только для администраторов.
        </p>
        <div className="flex justify-center">
          <Link 
            to="/" 
            className="flex items-center justify-center bg-white text-purple-600 px-6 py-3 rounded-full font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-purple-100"
          >
            <FaHome className="mr-2" />
            На главную
          </Link>
        </div>
      </div>
      <footer className="mt-12 text-sm text-white text-opacity-80">
        © 2024 LocalPay. Все права защищены.
      </footer>
    </div>
  );
};

export default UserRoleWarningPage;