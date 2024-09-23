import React, { useEffect, useState } from "react";
import {
  FaUser,
  FaMoneyBillWave,
  FaCalendarAlt,
  FaListAlt,
  FaChevronLeft,
  FaChevronRight,
  FaSignInAlt,
  FaDownload,
} from "react-icons/fa";
import axios from "axios";
import { Link } from "react-router-dom";
import { BACKEND_API_BASE_URL } from "../../config";
import { jwtDecode } from "jwt-decode";
import useRoleRedirect from "../../hooks/useRoleRedirect";
import api from "../../utils/api";
import { DecodedToken } from "../../components/DecodedToken";

interface UserInfo {
  surname: string;
  name: string;
  date_reg: string;
  available_balance: number;
  region: string;
  spent_money: number;
  login: string;
}

interface Payment {
  id: number;
  payment_date: string;
  money: number;
  payment_number: string;
  ls_abon: string;
  payment_status: string;
}

interface PaymentsResponse {
  payments: Payment[];
  total: number;
  next_cursor: string | null;
  per_page: number;
}

const UserProfile: React.FC = () => {
  useRoleRedirect(["user"]);

  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [currentCursor, setCurrentCursor] = useState<string | null>(null);
  const [cursorHistory, setCursorHistory] = useState<(string | null)[]>([null]);
  const [perPage, setPerPage] = useState(10);
  const [totalItems, setTotalItems] = useState(0);

  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showErrorPopup, setShowErrorPopup] = useState<boolean>(false);

  const [reportType, setReportType] = useState<"localpay" | "planup-localpay">(
    "localpay"
  );

  const formatDateForDisplay = (dateString: string): string => {
    const date = new Date(dateString);
    date.setDate(date.getDate() + 1); // Устанавливаем дату на завтра
    return date.toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  };

  const formatDate = (date: string): string => {
    const [year, month, day] = date.split("-");
    return `${day}/${month}/${year}`;
  };

  const handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedDateStr = e.target.value;
    const selectedDate = new Date(selectedDateStr);

    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (selectedDate > tomorrow) {
      setErrorMessage("Нельзя выбирать дату в будущем. Максимум - завтра.");
      setShowErrorPopup(true);
    } else {
      setErrorMessage(null);
      setShowErrorPopup(false);
      setEndDate(selectedDateStr);
    }
  };

  const getColorClass = (status: string) => {
    switch (status) {
      case "Выполнен":
        return "font-bold text-white drop-shadow-md"; // зеленый цвет
      case "Аннулирован":
        return "font-bold text-red-500 drop-shadow-md"; // красный цвет
      default:
        return "text-white"; // стандартный белый цвет
    }
  };

  useEffect(() => {
    const fetchUserInfo = async () => {
      const token = localStorage.getItem("token");
      if (token) {
        try {
          const decodedToken = jwtDecode<DecodedToken>(token);
          const userId = decodedToken.id;
          const response = await axios.get(
            `${BACKEND_API_BASE_URL}/user_by_id/${userId}`,
            {
              headers: { Authorization: `Bearer ${token}` },
            }
          );
          setUserInfo(response.data);
          fetchPayments(response.data.login, null);
        } catch (error) {
          console.error("Error fetching user info:", error);
        }
      }
    };

    fetchUserInfo();
  }, []);

  const fetchPayments = async (
    login: string,
    cursor: string | null,
    itemsPerPage: number = perPage,
    direction: "next" | "prev" | "initial" = "initial"
  ) => {
    const token = localStorage.getItem("token");
    if (!token) {
      console.error("No token found");
      return;
    }

    try {
      const params = new URLSearchParams({
        login,
        per_page: itemsPerPage.toString(),
        ...(startDate && { start_date: formatDate(startDate) }),
        ...(endDate && { end_date: formatDate(endDate) }),
        ...(cursor && { cursor }),
      });

      const response = await axios.get<PaymentsResponse>(
        `${BACKEND_API_BASE_URL}/payments_by_user?${params.toString()}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setPayments(response.data.payments);
      setTotalItems(response.data.total);

      if (direction === "next") {
        setCursorHistory((prevHistory) => [...prevHistory, cursor!]);
      } else if (direction === "prev") {
        setCursorHistory((prevHistory) => prevHistory.slice(0, -1));
      }

      setCurrentCursor(response.data.next_cursor);
    } catch (error) {
      console.error("Error fetching payments:", error);
    }
  };

  const handlePageChange = (direction: "next" | "prev") => {
    if (userInfo) {
      if (direction === "next" && currentCursor) {
        fetchPayments(userInfo.login, currentCursor, perPage, "next");
      } else if (direction === "prev") {
        const previousCursor = cursorHistory[cursorHistory.length - 2];
        fetchPayments(userInfo.login, previousCursor, perPage, "prev");
      }
    }
  };

  const handlePerPageChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newPerPage = parseInt(event.target.value);
    setPerPage(newPerPage);
    if (userInfo) {
      fetchPayments(userInfo.login, null, newPerPage, "initial");
      setCursorHistory([]);
    }
  };

  const handleDownloadReport = async () => {
    if (!userInfo) {
      console.error("User info not available");
      return;
    }

    try {
      let url = "";
      if (reportType === "localpay") {
        url = "/export-single-user-payments/";
      } else {
        url = "/planup-localpay-comparison";
      }

      const response = await api.get(url, {
        params: {
          login: userInfo.login,
          start_date: startDate ? formatDate(startDate) : undefined,
          end_date: endDate ? formatDate(endDate) : undefined,
        },
        responseType: "blob",
      });

      const blob = new Blob([response.data], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.setAttribute(
        "download",
        `Отчет ${reportType === "localpay" ? "LocalPay" : "PlanUp/LocalPay"} ${
          userInfo.login
        }.xlsx`
      );
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (error) {
      console.error("Error downloading report:", error);
    }
  };

  if (!userInfo) {
    return <div className="text-center text-white">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-400 to-blue-600 flex flex-col items-center justify-center text-white p-4">
      <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-3xl p-8 shadow-2xl w-full max-w-4xl">
        <h1 className="text-4xl font-bold mb-6 text-center">
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-purple-100 drop-shadow-md">
            Личный кабинет
          </span>
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white bg-opacity-20 rounded-xl p-4">
            <h2 className="text-xl font-semibold mb-4 flex items-center drop-shadow-md">
              <FaUser className="mr-2 text-black drop-shadow-md" /> Информация о
              пользователе
            </h2>
            <p>
              <strong>ФИО:</strong> {userInfo.name} {userInfo.surname}
            </p>
            <p>
              <strong>Регион:</strong> {userInfo.region}
            </p>
            <p>
              <strong>Логин:</strong> {userInfo.login}
            </p>
            <p>
              <strong>Дата регистрации:</strong>{" "}
              {new Date(userInfo.date_reg).toLocaleDateString()}
            </p>
          </div>
          <div className="bg-white bg-opacity-20 rounded-xl p-4">
            <h2 className="text-xl font-semibold mb-4 flex items-center drop-shadow-md">
              <FaMoneyBillWave className="mr-2 text-green-700" /> Финансовая
              информация
            </h2>
            <p>
              <strong>Доступный баланс:</strong> {userInfo.available_balance}{" "}
              сом
            </p>
            <p>
              <strong>Потраченные средства:</strong> -
              {Math.abs(userInfo.spent_money)} сом
            </p>
          </div>
        </div>

        <div className="bg-white bg-opacity-20 rounded-xl p-4">
          <h2 className="text-xl font-semibold mb-4 flex items-center drop-shadow-md">
            <FaListAlt className="mr-2 drop-shadow-md" /> История платежей
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left">
                  <th className="p-2">Дата</th>
                  <th className="p-2">Сумма</th>
                  <th className="p-2">Номер платежа</th>
                  <th className="p-2">Лицевой счет</th>
                  <th className="p-2">Статус</th>
                </tr>
              </thead>
              <tbody>
                {payments.map((payment) => (
                  <tr
                    key={payment.id}
                    className="border-t border-white border-opacity-20"
                  >
                    <td className="p-2">
                      {new Date(payment.payment_date).toLocaleString()}
                    </td>
                    <td className="p-2">{payment.money} сом</td>
                    <td className="p-2">{payment.payment_number}</td>
                    <td className="p-2">{payment.ls_abon}</td>
                    <td
                      className={`px-4 py-2 whitespace-nowrap text-sm ${getColorClass(
                        payment.payment_status
                      )}`}
                    >
                      {payment.payment_status}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="mt-4 flex flex-col sm:flex-row justify-between items-center">
          <div className="flex items-center mb-2 sm:mb-0">
            <span className="text-white mr-2">Показывать по:</span>
            <select
              value={perPage}
              onChange={handlePerPageChange}
              className="bg-white bg-opacity-20 text-white rounded-md px-2 py-1"
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
          <nav
            className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px"
            aria-label="Pagination"
          >
            <button
              onClick={() => handlePageChange("prev")}
              className="relative inline-flex items-center px-4 py-2 rounded-l-md border border-purple-300 bg-white bg-opacity-20 text-sm font-medium text-white hover:bg-purple-500 transition-colors duration-300"
              disabled={cursorHistory.length === 0}
            >
              <FaChevronLeft />
            </button>
            <button
              onClick={() => handlePageChange("next")}
              className="relative inline-flex items-center px-4 py-2 rounded-r-md border border-purple-300 bg-white bg-opacity-20 text-sm font-medium text-white hover:bg-purple-500 transition-colors duration-300"
              disabled={!currentCursor}
            >
              <FaChevronRight />
            </button>
          </nav>
        </div>
      </div>

      <div className="bg-white bg-opacity-20 rounded-xl p-4 mt-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center drop-shadow-md">
          <FaDownload className="mr-2 text-green-600" /> Скачать отчет
        </h2>
        <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-4">
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="bg-white bg-opacity-20 rounded-md px-3 py-2 text-white"
            placeholder="Начальная дата"
          />
          <input
            type="date"
            value={endDate}
            onChange={handleEndDateChange}
            className="bg-white bg-opacity-20 rounded-md px-3 py-2 text-white"
            placeholder="Конечная дата"
          />
          <select
            value={reportType}
            onChange={(e) =>
              setReportType(e.target.value as "localpay" | "planup-localpay")
            }
            className="bg-white bg-opacity-20 rounded-md px-3 py-2 text-white"
          >
            <option value="localpay">LocalPay</option>
            <option value="planup-localpay">PlanUp/LocalPay</option>
          </select>
          <button
            onClick={handleDownloadReport}
            className="bg-white text-green-600 px-4 py-2 rounded-full font-semibold transition duration-300 ease-in-out transform hover:scale-105 hover:bg-purple-100"
          >
            Скачать отчет
          </button>
        </div>
      </div>

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
    </div>
  );
};

export default UserProfile;
