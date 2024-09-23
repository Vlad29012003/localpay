import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { FaDownload, FaHome } from "react-icons/fa";
import { BACKEND_API_BASE_URL } from "../../config";
import useRoleRedirect from "../../hooks/useRoleRedirect";
import { DecodedToken } from "../../components/DecodedToken";
import { jwtDecode } from "jwt-decode";
import api from "../../utils/api";

type ReportType =
  | "single-user-payments"
  | "all-user-payments"
  | "all-users-info";

interface User {
  login: string;
}

const regions = [
  { value: "Чуйская", label: "Чуй" },
  { value: "Иссык-кульская", label: "Иссык-Куль" },
  { value: "Нарынская", label: "Нарын" },
  { value: "Джалал-Абадская", label: "Джалал-Абад" },
  { value: "Баткенская", label: "Баткен" },
  { value: "Ошская", label: "Ош" },
  { value: "Таласская", label: "Талас" },
];

const ReportsPage: React.FC = () => {
  useRoleRedirect(["admin", "supervisor"]);

  const [reportType, setReportType] = useState<ReportType | null>(null);
  const [startDate, setStartDate] = useState<string | null>(null);
  const [endDate, setEndDate] = useState<string | null>(null);
  const [login, setLogin] = useState<string>("");
  const [users, setUsers] = useState<User[]>([]);
  const [filteredUsers, setFilteredUsers] = useState<User[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showErrorPopup, setShowErrorPopup] = useState<boolean>(false);
  const [selectedRegion, setSelectedRegion] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [singleUserReportType, setSingleUserReportType] = useState<
    "localpay" | "planup-localpay"
  >("localpay");

  useEffect(() => {
    fetchUsers();
  }, []);

  const formatDateForDisplay = (dateString: string): string => {
    const date = new Date(dateString);
    date.setDate(date.getDate() + 1); // Устанавливаем дату на завтра
    return date.toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  };

  const fetchUsers = useCallback(async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No token available");

      const response = await axios.get(`${BACKEND_API_BASE_URL}/users`, {
        params: { page: 1, per_page: 10000000 },
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      setUsers(response.data.users);
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  }, []);

  const handleLoginChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setLogin(value);
    setFilteredUsers(
      users.filter((user) =>
        user.login.toLowerCase().includes(value.toLowerCase())
      )
    );
  };

  const formatDate = (date: string): string => {
    const [year, month, day] = date.split("-");
    return `${day}/${month}/${year}`;
  };

  const handleDownload = () => {
    setIsLoading(true); // Устанавливаем isLoading в true перед началом загрузки
    let url = "";

    if (reportType === "single-user-payments") {
      const query = new URLSearchParams();
      if (login) query.append("login", login);
      if (startDate) query.append("start_date", formatDate(startDate));
      if (endDate) query.append("end_date", formatDate(endDate));
      
      if (singleUserReportType === "localpay") {
        url = `/export-single-user-payments?${query.toString()}`;
      } else {
        url = `/planup-localpay-comparison?${query.toString()}`;
      }
    } else if (reportType === "all-user-payments") {
      const query = new URLSearchParams();
      if (startDate) query.append("start_date", formatDate(startDate));
      if (endDate) query.append("end_date", formatDate(endDate));
      if (selectedRegion) query.append("region", selectedRegion);
      url = `/export-all-user-payments?${query.toString()}`;
    } else if (reportType === "all-users-info") {
      url = "/export-all-users-info";
    }

    api
      .get(url, { responseType: "blob" })
      .then((response) => {
        const blob = new Blob([response.data], {
          type: response.headers["content-type"],
        });
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = downloadUrl;
        link.download = "Отчет.xlsx";
        document.body.appendChild(link);
        link.click();
        link.remove();
        setIsLoading(false);
      })
      .catch((error) => {
        console.error("Error downloading report:", error);
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  const LoadingPopup: React.FC = () => (
    <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
      <div className="bg-white bg-opacity-90 p-6 rounded-lg shadow-lg text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-600 mx-auto mb-4"></div>
        <p className="text-purple-600 font-semibold">Загрузка отчета...</p>
      </div>
    </div>
  );

  const handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedDateStr = e.target.value;

    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (selectedDateStr > tomorrow.toISOString().split("T")[0]) {
      setErrorMessage("Нельзя выбирать дату в будущем. Максимум - завтра.");
      setShowErrorPopup(true);
    } else {
      setErrorMessage(null);
      setShowErrorPopup(false);
      setEndDate(selectedDateStr);
    }
  };

  const renderPreview = () => {
    if (reportType === "single-user-payments") {
      return (
        <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-3xl p-6 shadow-xl mt-8">
          <h3 className="text-2xl font-semibold mb-4 text-center">
            Предварительный просмотр отчета
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-purple-200 bg-opacity-50">
                  <th className="border border-purple-300 p-2 text-left">
                    ЛС абонента
                  </th>
                  <th className="border border-purple-300 p-2 text-left">
                    LocalPay сумма
                  </th>
                  <th className="border border-purple-300 p-2 text-left">
                    PlanUp сумма
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr className="bg-white bg-opacity-20">
                  <td className="border border-purple-300 p-2">12345</td>
                  <td className="border border-purple-300 p-2">1000</td>
                  <td className="border border-purple-300 p-2">950</td>
                </tr>
                <tr className="bg-white bg-opacity-20">
                  <td className="border border-purple-300 p-2">67890</td>
                  <td className="border border-purple-300 p-2">2000</td>
                  <td className="border border-purple-300 p-2">1950</td>
                </tr>
                <tr className="bg-white bg-opacity-20">
                  <td className="border border-purple-300 p-2">54321</td>
                  <td className="border border-purple-300 p-2">1500</td>
                  <td className="border border-purple-300 p-2 text-white font-bold drop-shadow-md">
                    ТАКОЙ ПЛАТЕЖ ОТСУТСТВУЕТ
                  </td>
                </tr>
              </tbody>
              <tfoot>
                <tr className="bg-purple-200 bg-opacity-50">
                  <td className="border border-purple-300 p-2 font-bold">
                    Итого:
                  </td>
                  <td className="border border-purple-300 p-2 font-bold">
                    4500
                  </td>
                  <td className="border border-purple-300 p-2 font-bold">
                    2900
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
          <p className="mt-4 text-white">
            <span className="font-bold">Период:</span>{" "}
            {startDate || "за все время"} - {endDate || "за все время"}
          </p>
          <p className="mt-2 text-white">
            <span className="font-bold">Логин пользователя:</span> {login}
          </p>
        </div>
      );
    } else if (reportType === "all-user-payments") {
      return (
        <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-3xl p-6 shadow-xl mt-8">
          <h3 className="text-2xl font-semibold mb-4 text-center">
            Предварительный просмотр отчета
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-purple-200 bg-opacity-50">
                  <th className="border border-purple-300 p-2 text-left">
                    Номер платежа
                  </th>
                  <th className="border border-purple-300 p-2 text-left">
                    Дата проведения
                  </th>
                  <th className="border border-purple-300 p-2 text-left">
                    Лицевой счет
                  </th>
                  <th className="border border-purple-300 p-2 text-left">
                    Сумма
                  </th>
                  <th className="border border-purple-300 p-2 text-left">
                    Статус платежа
                  </th>
                  <th className="border border-purple-300 p-2 text-left">
                    ID пользователя
                  </th>
                  <th className="border border-purple-300 p-2 text-left">
                    Аннулирование
                  </th>
                  <th className="border border-purple-300 p-2 text-left">
                    Комментарий
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr className="bg-white bg-opacity-20">
                  <td className="border border-purple-300 p-2">123456</td>
                  <td className="border border-purple-300 p-2">2023-07-01</td>
                  <td className="border border-purple-300 p-2">12345</td>
                  <td className="border border-purple-300 p-2">1000</td>
                  <td className="border border-purple-300 p-2">Выполнен</td>
                  <td className="border border-purple-300 p-2">1</td>
                  <td className="border border-purple-300 p-2">False</td>
                  <td className="border border-purple-300 p-2">
                    Купил биткоин
                  </td>
                </tr>
                <tr className="bg-white bg-opacity-20">
                  <td className="border border-purple-300 p-2">654321</td>
                  <td className="border border-purple-300 p-2">2023-07-02</td>
                  <td className="border border-purple-300 p-2">67890</td>
                  <td className="border border-purple-300 p-2">2000</td>
                  <td className="border border-purple-300 p-2">Выполнен</td>
                  <td className="border border-purple-300 p-2">2</td>
                  <td className="border border-purple-300 p-2">False</td>
                  <td className="border border-purple-300 p-2">Купил хомяка</td>
                </tr>
              </tbody>
              <tfoot>
                <tr className="bg-purple-200 bg-opacity-50">
                  <td
                    colSpan={3}
                    className="border border-purple-300 p-2 font-bold"
                  >
                    Итого:
                  </td>
                  <td className="border border-purple-300 p-2 font-bold">
                    3000
                  </td>
                  <td colSpan={4} className="border border-purple-300 p-2"></td>
                </tr>
              </tfoot>
            </table>
          </div>
          <p className="mt-4 text-white">
            <span className="font-bold">Период:</span>{" "}
            {startDate || "за все время"} - {endDate || "за все время"}
          </p>
          {selectedRegion && (
            <p className="mt-2 text-white">
              <span className="font-bold">Регион:</span> {selectedRegion}
            </p>
          )}
        </div>
      );
    } else if (reportType === "all-users-info") {
      return (
        <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-3xl p-6 shadow-xl mt-8">
          <h3 className="text-2xl font-semibold mb-4 text-center">
            Предварительный просмотр отчета
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-purple-200 bg-opacity-50">
                  <th className="border border-purple-300 p-2 text-left">
                    Имя
                  </th>
                  <th className="border border-purple-300 p-2 text-left">
                    Фамилия
                  </th>
                  <th className="border border-purple-300 p-2 text-left">
                    Логин
                  </th>
                  <th className="border border-purple-300 p-2 text-left">
                    Доступный Баланс
                  </th>
                  <th className="border border-purple-300 p-2 text-left">
                    Потрачено
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr className="bg-white bg-opacity-20">
                  <td className="border border-purple-300 p-2">Федор</td>
                  <td className="border border-purple-300 p-2">Достоевский</td>
                  <td className="border border-purple-300 p-2">dosya</td>
                  <td className="border border-purple-300 p-2">5000</td>
                  <td className="border border-purple-300 p-2">-1500</td>
                </tr>
                <tr className="bg-white bg-opacity-20">
                  <td className="border border-purple-300 p-2">Александр</td>
                  <td className="border border-purple-300 p-2">Пушкин</td>
                  <td className="border border-purple-300 p-2">pushka777</td>
                  <td className="border border-purple-300 p-2">5000</td>
                  <td className="border border-purple-300 p-2">-1500</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex flex-col items-center justify-center text-white p-4">
      <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-3xl p-8 shadow-2xl w-full max-w-4xl">
        <h1 className="text-4xl font-bold mb-6 text-center">
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-purple-100">
            Выгрузка отчетов
          </span>
        </h1>
        <div className="space-y-4 mb-8">
          <div>
            <label className="block text-lg font-semibold mb-2">
              Тип отчета:
            </label>
            <select
              className="w-full bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg p-3 text-white"
              value={reportType || ""}
              onChange={(e) => setReportType(e.target.value as ReportType)}
            >
              <option value="" disabled>
                Выберите тип отчета
              </option>
              <option value="single-user-payments">
                Отчет по платежам одного пользователя
              </option>
              <option value="all-user-payments">
                Отчет по платежам всех пользователей
              </option>
              <option value="all-users-info">
                Отчет по всем пользователям
              </option>
            </select>
          </div>
          {reportType === "all-user-payments" && (
            <>
              <div>
                <label className="block text-lg font-semibold mb-2">
                  Дата начала:
                </label>
                <input
                  type="date"
                  className="w-full bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg p-3 text-white"
                  value={startDate || ""}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-lg font-semibold mb-2">
                  Дата окончания:
                </label>
                <input
                  type="date"
                  className="w-full bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg p-3 text-white"
                  value={endDate || ""}
                  onChange={handleEndDateChange}
                />
              </div>
              <div>
                <label className="block text-lg font-semibold mb-2">
                  Регион:
                </label>
                <select
                  className="w-full bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg p-3 text-white"
                  value={selectedRegion}
                  onChange={(e) => setSelectedRegion(e.target.value)}
                >
                  <option value="">Выберите регион</option>
                  {regions.map((region) => (
                    <option key={region.value} value={region.value}>
                      {region.label}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}
          {reportType === "single-user-payments" && (
            <>
              <div>
                <label className="block text-lg font-semibold mb-2">
                  Тип отчета по платежам:
                </label>
                <select
                  className="w-full bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg p-3 text-white"
                  value={singleUserReportType}
                  onChange={(e) =>
                    setSingleUserReportType(
                      e.target.value as "localpay" | "planup-localpay"
                    )
                  }
                >
                  <option value="localpay">LocalPay</option>
                  <option value="planup-localpay">PlanUp/LocalPay</option>
                </select>
              </div>
              <div className="relative">
                <label className="block text-lg font-semibold mb-2">
                  Логин пользователя:
                </label>
                <input
                  type="text"
                  className="w-full bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg p-3 text-white"
                  value={login}
                  onChange={handleLoginChange}
                  onFocus={() => setFilteredUsers(users)}
                />
                {filteredUsers.length > 0 && (
                  <ul className="z-50 w-full bg-white bg-opacity-90 border border-white border-opacity-30 rounded-lg shadow-lg max-h-60 overflow-y-auto bottom-full mb-1">
                    {filteredUsers.map((user, index) => (
                      <li
                        key={index}
                        className="p-2 hover:bg-purple-200 cursor-pointer text-purple-800"
                        onClick={() => {
                          setLogin(user.login);
                          setFilteredUsers([]);
                        }}
                      >
                        {user.login}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              <div>
                <label className="block text-lg font-semibold mb-2">
                  Дата начала:
                </label>
                <input
                  type="date"
                  className="w-full bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg p-3 text-white"
                  value={startDate || ""}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-lg font-semibold mb-2">
                  Дата окончания:
                </label>
                <input
                  type="date"
                  className="w-full bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg p-3 text-white"
                  value={endDate || ""}
                  onChange={handleEndDateChange}
                />
              </div>
            </>
          )}
        </div>
        <button
          className="w-full bg-white text-purple-600 px-6 py-3 rounded-full font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-purple-100 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
          onClick={handleDownload}
          disabled={!!errorMessage || isLoading}
        >
          {isLoading ? (
            <span className="animate-pulse">Загрузка...</span>
          ) : (
            <>
              <FaDownload className="mr-2" />
              Скачать отчет
            </>
          )}
        </button>
      </div>

      {renderPreview()}

      <Link
        to="/admin"
        className="mt-8 flex items-center justify-center bg-white text-blue-600 px-6 py-3 rounded-full font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-blue-100"
      >
        <FaHome className="mr-2" />
        Панель
      </Link>
      <footer className="mt-12 text-sm text-white text-opacity-80">
        © 2024 LocalPay. Все права защищены.
      </footer>

      {showErrorPopup && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div className="bg-red-500 text-white p-4 rounded-lg shadow-lg">
            <p>{errorMessage}</p>
            <p className="mt-2">
              Максимальная дата:{" "}
              {formatDateForDisplay(new Date().toISOString().split("T")[0])}
            </p>
            <button
              onClick={() => {
                setShowErrorPopup(false);
                setErrorMessage(null);
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                setEndDate(tomorrow.toISOString().split("T")[0]);
              }}
              className="mt-2 bg-white text-red-500 px-4 py-2 rounded hover:bg-red-100"
            >
              Закрыть
            </button>
          </div>
        </div>
      )}
      {isLoading && <LoadingPopup />}
    </div>
  );
};

export default ReportsPage;
