import React, { useEffect, useState } from "react";
import {
  FaUser,
  FaLock,
  FaGlobe,
  FaComment,
  FaUserShield,
  FaCheckCircle,
  FaMoneyBillWave,
  FaSignInAlt,
  FaTimes,
} from "react-icons/fa";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";
import { BACKEND_API_BASE_URL } from "../../config";
import useRoleRedirect from "../../hooks/useRoleRedirect";

const regions = [
  { value: "Чуйская", label: "Чуйская" },
  { value: "Иссык-кульская", label: "Иссык-кульская" },
  { value: "Нарынская", label: "Нарынская" },
  { value: "Джалал-Абадская", label: "Джалал-Абадская" },
  { value: "Баткенская", label: "Баткенская" },
  { value: "Ошская", label: "Ошская" },
  { value: "Таласская", label: "Таласская" },
];

interface SnackBarProps {
  message: string;
  type: "success" | "error";
  onClose: () => void;
}

const SnackBar: React.FC<SnackBarProps> = ({ message, type, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 10000);

    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div
      className={`fixed bottom-4 right-4 p-4 rounded-md shadow-lg flex items-center justify-between ${
        type === "success" ? "bg-green-500" : "bg-red-500"
      }`}
    >
      <span className="text-white mr-4">{message}</span>
      <button onClick={onClose} className="text-white focus:outline-none">
        <FaTimes />
      </button>
    </div>
  );
};

const RegisterUserPage: React.FC = () => {

  useRoleRedirect(['admin']);
  
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    surname: "",
    login: "",
    is_admin: false,
    access_to_payments: false,
    is_active: true,
    region: "",
    password: "",
    comment: "",
  });

  const [snackBar, setSnackBar] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem("token");
    if (!token) {
      console.error("No token found");
      return;
    }

    try {
      await axios.post(
        `${BACKEND_API_BASE_URL}/create_user`,
        {
          ...formData,
          available_balance: 0,
          spent_money: 0,
          refill: 0,
          write_off: 0,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );
      setSnackBar({ message: "Пользователь успешно создан", type: "success" });
      setTimeout(() => navigate("/admin"), 3000);
    } catch (error) {
      console.error("Error creating user:", error);
      setSnackBar({
        message: "Ошибка при создании пользователя",
        type: "error",
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-purple-700 flex flex-col items-center justify-center p-4">
      <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-md rounded-3xl p-8 shadow-2xl w-full max-w-2xl">
        <h1 className="text-5xl font-bold mb-8 text-center text-white">
          Регистрация пользователя
        </h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-white">
            <InputField
              name="name"
              label="Имя"
              icon={<FaUser />}
              value={formData.name}
              onChange={handleChange}
              placeholder="Введите имя"
            />
            <InputField
              name="surname"
              label="Фамилия"
              icon={<FaUser />}
              value={formData.surname}
              onChange={handleChange}
              placeholder="Введите фамилию"
            />
          </div>
          <InputField
            name="login"
            label="Логин"
            icon={<FaUser />}
            value={formData.login}
            onChange={handleChange}
            placeholder="Введите логин"
          />
          <InputField
            name="password"
            label="Пароль"
            icon={<FaLock />}
            type="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Введите пароль"
          />
          <div className="relative">
            <label
              htmlFor="region"
              className="block text-lg font-medium text-white mb-2"
            >
              Регион
            </label>
            <div className="relative">
              <FaGlobe className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white text-xl" />
              <select
                name="region"
                id="region"
                required
                className="w-full bg-white bg-opacity-20 text-white placeholder-opacity-50 focus:ring-2 focus:ring-purple-400 focus:border-transparent block pl-10 pr-4 py-3 border border-transparent rounded-xl text-lg"
                value={formData.region}
                onChange={handleChange}
              >
                <option value="" className='text-black'>Выберите регион</option>
                {regions.map((region) => (
                  <option key={region.value} value={region.value} className='text-black'>
                    {region.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="relative">
            <label
              htmlFor="comment"
              className="block text-lg font-medium text-white mb-2"
            >
              Комментарий
            </label>
            <div className="relative">
              <FaComment className="absolute left-3 top-3 text-white text-xl" />
              <textarea
                name="comment"
                id="comment"
                rows={4}
                className="w-full bg-white bg-opacity-20 text-white placeholder-opacity-50 placeholder:text-white/75 focus:ring-2 focus:ring-purple-400 focus:border-transparent block pl-10 pr-4 py-3 border border-transparent rounded-xl text-lg"
                placeholder="Введите комментарий"
                value={formData.comment}
                onChange={handleChange}
              ></textarea>
            </div>
          </div>
          <div className="space-y-4">
            <CheckboxField
              name="is_admin"
              label="Администратор"
              icon={<FaUserShield />}
              checked={formData.is_admin}
              onChange={handleChange}
            />
            <CheckboxField
              name="access_to_payments"
              label="Доступ к платежам"
              icon={<FaMoneyBillWave />}
              checked={formData.access_to_payments}
              onChange={handleChange}
            />
            <CheckboxField
              name="is_active"
              label="Активный пользователь"
              icon={<FaCheckCircle />}
              checked={formData.is_active}
              onChange={handleChange}
            />
          </div>
          <button
            type="submit"
            className="bg-opacity-10 backdrop-filter backdrop-blur-md w-full py-4 px-6 bg-purple-600 hover:bg-purple-600 focus:ring-purple-500 focus:ring-offset-purple-200 text-white transition ease-in duration-200 text-center text-lg font-semibold shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2 rounded-xl"
          >
            Зарегистрировать
          </button>
        </form>
      </div>
      <nav className="mt-8 flex justify-center space-x-6">
        <Link
          to="/admin"
          className="flex items-center justify-center bg-white text-blue-600 px-6 py-3 rounded-full font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-purple-100"
        >
          <FaSignInAlt className="mr-2" />
          Админ Панель
        </Link>
      </nav>

      <footer className="mt-12 text-sm text-white text-opacity-80">
        © 2024 LocalPay. Все права защищены.
      </footer>

      {snackBar && (
        <SnackBar
          message={snackBar.message}
          type={snackBar.type}
          onClose={() => setSnackBar(null)}
        />
      )}
    </div>
  );
};

interface InputFieldProps {
  name: string;
  label: string;
  icon: React.ReactNode;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder: string;
  type?: string;
}

const InputField: React.FC<InputFieldProps> = ({
  name,
  label,
  icon,
  value,
  onChange,
  placeholder,
  type = "text",
}) => (
  <div className="relative">
    <label htmlFor={name} className="block text-lg font-medium text-white mb-2">
      {label}
    </label>
    <div className="relative">
      <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white text-xl">
        {icon}
      </div>
      <input
        type={type}
        name={name}
        id={name}
        required
        className="w-full bg-white bg-opacity-20 text-white placeholder-white placeholder-opacity-50 focus:ring-2 focus:ring-purple-400 focus:border-transparent block pl-10 pr-4 py-3 border border-transparent rounded-xl text-lg"
        placeholder={placeholder}
        value={value}
        onChange={onChange}
      />
    </div>
  </div>
);

interface CheckboxFieldProps {
  name: string;
  label: string;
  icon: React.ReactNode;
  checked: boolean;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const CheckboxField: React.FC<CheckboxFieldProps> = ({
  name,
  label,
  icon,
  checked,
  onChange,
}) => (
  <div className="flex items-center space-x-3">
    <div className="relative inline-block">
      <input
        type="checkbox"
        name={name}
        id={name}
        className="hidden"
        checked={checked}
        onChange={onChange}
      />
      <label
        htmlFor={name}
        className="flex items-center justify-center w-6 h-6 bg-white bg-opacity-20 border-1 border-purple-400 rounded-md cursor-pointer transition-colors duration-200 ease-in-out"
      >
        {checked && (
          <svg
            className="w-4 h-4 text-white/60 fill-current"
            viewBox="0 0 20 20"
          >
            <path d="M0 11l2-2 5 5L18 3l2 2L7 18z" />
          </svg>
        )}
      </label>
    </div>
    <label
      htmlFor={name}
      className="flex items-center text-lg text-white cursor-pointer"
    >
      <span className="mr-2">{icon}</span>
      {label}
    </label>

  </div>
);

export default RegisterUserPage;
