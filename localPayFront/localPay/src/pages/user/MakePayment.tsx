import React, { useState } from "react";
import { FaMoneyBillWave, FaSignInAlt } from "react-icons/fa";
import { Link } from "react-router-dom";
import useRoleRedirect from "../../hooks/useRoleRedirect";

const MakePayment: React.FC = () => {

  useRoleRedirect(['user']);
  
  const [lsAbon, setLsAbon] = useState("");
  const [money, setMoney] = useState("");
  const [message, setMessage] = useState<{
    text: string;
    isError: boolean;
  } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);

    const token = localStorage.getItem("token");
    if (!token) {
      setMessage({
        text: "Ошибка авторизации. Попробуйте войти снова.",
        isError: true,
      });
      return;
    }

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/create_payment?ls_abon=${lsAbon}&money=${money}`,
        {
          method: "POST",
          headers: {
            accept: "application/json",
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: "", // пустое тело запроса
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        let errorMessage = errorData.detail || "Ошибка при выполнении платежа";
        if (errorMessage === "Not enough money") {
          errorMessage = "Недостаточно средств на балансе";
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setMessage({ text: "Платеж успешно выполнен!", isError: false });
    } catch (error: any) {
      setMessage({
        text: `Ошибка при выполнении платежа: ${error.message}`,
        isError: true,
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-400 to-blue-600 flex flex-col items-center justify-center text-white p-4">
      <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-3xl p-8 shadow-2xl w-full max-w-md">
        <h1 className="text-4xl font-bold mb-6 text-center">
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-purple-100">
            Выполнить платеж
          </span>
        </h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="lsAbon" className="block text-sm font-medium mb-2">
              Лицевой счет
            </label>
            <input
              type="text"
              id="lsAbon"
              value={lsAbon}
              onChange={(e) => setLsAbon(e.target.value)}
              className="w-full px-4 py-2 rounded-full bg-white bg-opacity-20 text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-300"
              placeholder="Введите лицевой счет"
              required
            />
          </div>
          <div>
            <label htmlFor="money" className="block text-sm font-medium mb-2">
              Сумма
            </label>
            <input
              type="number"
              id="money"
              value={money}
              onChange={(e) => setMoney(e.target.value)}
              className="w-full px-4 py-2 rounded-full bg-white bg-opacity-20 text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-300"
              placeholder="Введите сумму"
              required
            />
          </div>
          <button
            type="submit"
            onClick={handleSubmit}
            className="w-full flex items-center justify-center bg-white text-green-600 px-6 py-3 rounded-full font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-green-100"
          >
            <FaMoneyBillWave className="mr-2" />
            Оплатить
          </button>
        </form>
      </div>
      {message && (
        <div
          className={`mt-6 px-4 py-2 rounded-full ${
            message.isError ? "bg-red-500" : "bg-green-500"
          } text-white text-center`}
        >
          {message.text}
        </div>
      )}
      <nav className="mt-8 flex justify-center space-x-6">
        <Link
          to="/user"
          className="flex items-center justify-center bg-white text-blue-600 px-6 py-3 rounded-full font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-purple-100"
        >
          <FaSignInAlt className="mr-2" />
          Панель юзера
        </Link>
      </nav>

      <footer className="mt-12 text-sm text-white text-opacity-80">
        © 2024 LocalPay. Все права защищены.
      </footer>
    </div>
  );
};

export default MakePayment;
