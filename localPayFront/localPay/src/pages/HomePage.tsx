import React from 'react';
import { Link } from 'react-router-dom';
import { FaUsers, FaChartBar, FaSignInAlt } from 'react-icons/fa';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex flex-col items-center justify-center text-white p-4">
      <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-3xl p-8 shadow-2xl">
        <h1 className="text-6xl font-bold mb-6 text-center">
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-purple-100">
            LocalPay
          </span>
        </h1>
        <p className="text-xl text-center mb-8">
          Добро пожаловать в систему управления локальными платежами
        </p>
        <nav className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-6">
          
          <Link 
            to="/login" 
            className="flex items-center justify-center bg-white text-green-600 px-6 py-3 rounded-full font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-green-100"
          >
            <FaSignInAlt className="mr-2" />
            Логин
          </Link>
        </nav>
      </div>
      <footer className="mt-12 text-sm text-white text-opacity-80">
        © 2024 LocalPay. Все права защищены.
      </footer>
    </div>
  );
};

export default HomePage;
