import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { FaUser, FaLock } from 'react-icons/fa';
import {jwtDecode} from 'jwt-decode';
import { BACKEND_API_BASE_URL } from '../config';
import { DecodedToken } from '../components/DecodedToken';


const LoginPage: React.FC = () => {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');

    try {
      const response = await axios.post(`${BACKEND_API_BASE_URL}/token`, new URLSearchParams({
        grant_type: '',
        username: login,
        password: password,
        scope: '',
        client_id: '',
        client_secret: '',
      }), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'accept': 'application/json'
        }
      });

      const { access_token } = response.data;
      localStorage.setItem('token', access_token);

      const decodedToken: DecodedToken = jwtDecode(access_token);
      const userRole = decodedToken.role;
      console.log(decodedToken)
      console.log(userRole)

      if (userRole === 'supervisor') {
        navigate('/supervisor');
      } else if (userRole === 'admin') {
        navigate('/admin');
      } else if (userRole === 'user') {
        navigate('/user');
      } else {
        setError('Неизвестная роль пользователя');
      }
    } catch (err) {
      setError('Неверный логин или пароль');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex flex-col items-center justify-center text-white p-4">
      <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-3xl p-8 shadow-2xl w-full max-w-md">
        <h1 className="text-4xl font-bold mb-6 text-center">
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-purple-100">
            LocalPay
          </span>
        </h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="relative">
            <FaUser className="absolute top-3 left-3 text-purple-300" />
            <input
              type="text"
              placeholder="Логин"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              className="w-full bg-white bg-opacity-20 rounded-full py-2 px-10 text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-300"
            />
          </div>
          <div className="relative">
            <FaLock className="absolute top-3 left-3 text-purple-300" />
            <input
              type="password"
              placeholder="Пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-white bg-opacity-20 rounded-full py-2 px-10 text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-300"
            />
          </div>
          {error && (
            <p className="text-red-300 text-center">{error}</p>
          )}
          <button
            type="submit"
            className="w-full bg-white text-purple-600 py-2 rounded-full font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-purple-100"
          >
            Войти
          </button>
        </form>
      </div>
      <footer className="mt-12 text-sm text-white text-opacity-80">
        © 2024 LocalPay. Все права защищены.
      </footer>
    </div>
  );
};

export default LoginPage;
