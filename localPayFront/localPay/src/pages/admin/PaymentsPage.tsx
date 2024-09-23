import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { FaChevronLeft, FaChevronRight, FaEdit, FaPlus } from "react-icons/fa";
import { Link } from "react-router-dom";
import { BACKEND_API_BASE_URL } from "../../config";
import { format } from "date-fns";
import useRoleRedirect from "../../hooks/useRoleRedirect";
import { jwtDecode } from "jwt-decode";

interface Payment {
  id: number;
  payment_accept: string;
  money: number;
  user_id: number;
  annulment: boolean;
  document_number: string | null;
  updated_at: string;
  payment_date: string;
  payment_number: string;
  ls_abon: string;
  payment_status: string;
  comment: string | null;
  name: string; // Добавленные свойства
  surname: string; // Добавленные свойства
  FullName: string;
}

interface User {
  id: number;
  name: string;
  surname: string;
}

const PaymentsPage: React.FC = () => {
  useRoleRedirect(["admin", "supervisor"]);

  const [payments, setPayments] = useState<Payment[]>([]);
  const [cursor, setCursor] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState<Payment | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [perPage, setPerPage] = useState(10);
  const [totalPayments, setTotalPayments] = useState(0);

  const [cursorHistory, setCursorHistory] = useState<(number | null)[]>([null]);

  const [startDateFilter, setStartDateFilter] = useState("");
  const [endDateFilter, setEndDateFilter] = useState("");
  const [lsFilter, setLsFilter] = useState("");
  const [nameFilter, setNameFilter] = useState("");

  const [userRole, setUserRole] = useState<string>("");

  const fetchUserById = async (userId: number): Promise<User | null> => {
    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No token available");

      const response = await axios.get(
        `${BACKEND_API_BASE_URL}/user_by_id/${userId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      return response.data as User;
    } catch (error) {
      console.error("Ошибка при получении пользователя:", error);
      return null;
    }
  };

  const getUserRole = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (token) {
      const decodedToken: any = jwtDecode(token);
      setUserRole(decodedToken.role);
    }
  }, []);

  useEffect(() => {
    getUserRole();
  }, [getUserRole]);

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

  const fetchPayments = async (
    newCursor: number | null,
    direction: "next" | "prev" | "initial" = "initial"
  ) => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No token available");

      const params: any = {
        cursor: newCursor,
        per_page: perPage,
      };

      if (startDateFilter) {
        params.start_date = formatDateForBackend(startDateFilter);
      }
      if (endDateFilter) {
        params.end_date = formatDateForBackend(endDateFilter);
      }
      if (lsFilter) params.ls_abon = lsFilter;
      if (nameFilter) params.name = nameFilter;

      const response = await axios.get(`${BACKEND_API_BASE_URL}/payments`, {
      params,
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    const updatedPayments = response.data.payments.map((payment: Payment) => ({
      ...payment,
      name: payment.FullName.split(' ')[0],
      surname: payment.FullName.split(' ').slice(1).join(' ')
    }));

    setPayments(updatedPayments);
    setTotalPayments(response.data.total);

    if (direction === "next" || direction === "initial") {
      setCursorHistory((prev) => [...prev, newCursor]);
    }
    setCursor(response.data.next_cursor);
  } catch (error) {
    console.error("Ошибка при получении платежей:", error);
    setSnackbarMessage("Ошибка при загрузке платежей");
    setSnackbarOpen(true);
  }
  setLoading(false);
};

  useEffect(() => {
    fetchPayments(null);
  }, [perPage]);

  const handlePageChange = (direction: "next" | "prev") => {
    if (direction === "next" && cursor) {
      fetchPayments(cursor, "next");
    } else if (direction === "prev") {
      if (cursorHistory.length > 1) {
        const newHistory = cursorHistory.slice(0, -1);
        setCursorHistory(newHistory);
        const prevCursor = newHistory[newHistory.length - 1];
        fetchPayments(prevCursor, "prev");
      }
    }
  };

  const formatDateForBackend = (date: string) => {
    const [year, month, day] = date.split("-");
    return `${day}/${month}/${year}`;
  };

  const handleStartDateFilterChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setStartDateFilter(e.target.value);
  };

  const handleEndDateFilterChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setEndDateFilter(e.target.value);
  };

  const handleAccountFilterChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setLsFilter(e.target.value);
  };

  const handleNameFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNameFilter(e.target.value);
  };

  const applyFilters = () => {
    setCursor(null); // Сбрасываем курсор при применении новых фильтров
    fetchPayments(null);
  };

  const handleOpenDialog = (payment: Payment | null) => {
    setSelectedPayment(payment);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedPayment(null);
  };

  const handlePerPageChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newPerPage = Number(event.target.value);
    setPerPage(newPerPage);
    setCursorHistory([null]);
    setCursor(null);
    fetchPayments(null, "initial");
  };

  const handleSavePayment = async () => {
    if (selectedPayment) {
      try {
        const token = localStorage.getItem("token");
        if (!token) throw new Error("No token available");

        if (selectedPayment.id) {
          await axios.patch(
            `${BACKEND_API_BASE_URL}/update_payment/${selectedPayment.id}`,
            {
              payment_status: selectedPayment.payment_status,
              annulment: selectedPayment.annulment,
              comment: selectedPayment.comment,
            },
            {
              headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
              },
            }
          );
          setSnackbarMessage("Платеж успешно обновлен");
        } else {
          await axios.post(
            `${BACKEND_API_BASE_URL}/create_payment`,
            {
              ls_abon: selectedPayment.ls_abon,
              money: selectedPayment.money,
            },
            {
              headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
              },
            }
          );
          setSnackbarMessage("Платеж успешно создан");
        }
        setSnackbarOpen(true);
        handleCloseDialog();
        fetchPayments(null, "initial");
      } catch (error) {
        console.error("Ошибка при сохранении платежа:", error);
        setSnackbarMessage("Ошибка при сохранении платежа");
        setSnackbarOpen(true);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex flex-col items-center justify-start p-4">
      <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-3xl p-8 shadow-2xl w-full max-w-6xl">
        <h1 className="text-4xl font-bold mb-8 text-center">
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-purple-100 drop-shadow-md">
            Управление платежами
          </span>
        </h1>

        <div className="mb-6 bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-xl p-6 shadow-lg">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div>
              <label
                htmlFor="startDateFilter"
                className="block text-sm font-medium text-white mb-2 drop-shadow-md"
              >
                Дата начала
              </label>
              <input
                type="date"
                id="startDateFilter"
                value={startDateFilter}
                onChange={handleStartDateFilterChange}
                className="w-full px-3 py-2 bg-white bg-opacity-20 border border-purple-100 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-300 focus:border-transparent"
              />
            </div>
            <div>
              <label
                htmlFor="endDateFilter"
                className="block text-sm font-medium text-white mb-2 drop-shadow-md"
              >
                Дата конца
              </label>
              <input
                type="date"
                id="endDateFilter"
                value={endDateFilter}
                onChange={handleEndDateFilterChange}
                className="w-full px-3 py-2 bg-white bg-opacity-20 border border-purple-100 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-300 focus:border-transparent"
              />
            </div>
            <div>
              <label
                htmlFor="accountFilter"
                className="block text-sm font-medium text-white mb-2 drop-shadow-md"
              >
                Лицевой счет
              </label>
              <input
                type="text"
                id="accountFilter"
                value={lsFilter}
                onChange={handleAccountFilterChange}
                className="w-full px-3 py-2 bg-white bg-opacity-20 border border-purple-100 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-300 focus:border-transparent"
              />
            </div>
            <div>
              <label
                htmlFor="nameFilter"
                className="block text-sm font-medium text-white mb-2 drop-shadow-md"
              >
                ФИО
              </label>
              <input
                type="text"
                id="nameFilter"
                value={nameFilter}
                onChange={handleNameFilterChange}
                className="w-full px-3 py-2 bg-white bg-opacity-20 border border-purple-100 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-300 focus:border-transparent"
              />
            </div>
            <div>
              <label
                htmlFor="nameFilter"
                className="block text-sm font-medium text-white mb-2 drop-shadow-md"
              >
                Click here ^_^
              </label>
              <button
                onClick={applyFilters}
                className="relative inline-flex items-center px-4 py-2.5 rounded border border-purple-100 bg-white bg-opacity-20 text-sm font-medium text-white hover:bg-purple-300 transition-colors duration-300"
              >
                Применить фильтры
              </button>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-white"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white bg-opacity-20 rounded-xl overflow-hidden">
              <thead>
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-white uppercase tracking-wider drop-shadow-md">
                    ID
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-white uppercase tracking-wider drop-shadow-md">
                    Дата платежа
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-white uppercase tracking-wider drop-shadow-md">
                    Дата принятия
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-white uppercase tracking-wider drop-shadow-md">
                    Сумма
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-white uppercase tracking-wider drop-shadow-md">
                    Пользователь
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-white uppercase tracking-wider drop-shadow-md">
                    Аннулирован
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-white uppercase tracking-wider drop-shadow-md">
                    Номер платежа
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-white uppercase tracking-wider drop-shadow-md">
                    Лицевой счет
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-white uppercase tracking-wider drop-shadow-md">
                    Статус
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-white uppercase tracking-wider drop-shadow-md">
                    Обновлено
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-white uppercase tracking-wider drop-shadow-md">
                    Комментарий
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-white uppercase tracking-wider drop-shadow-md">
                    Номер документа
                  </th>
                  {userRole === "admin" && (
                    <th className="px-4 py-2 text-left text-xs font-medium text-white uppercase tracking-wider drop-shadow-md">
                      Действия
                    </th>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {payments.map((payment) => (
                  <tr key={payment.id}>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-white">
                      {payment.id}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-white">
                      {format(
                        new Date(payment.payment_date),
                        "dd/MM/yyyy hh:mm:ss a"
                      )}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-white">
                      {format(
                        new Date(payment.payment_accept),
                        "dd/MM/yyyy hh:mm:ss a"
                      )}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-white">
                      {payment.money}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-white">
                      {payment.name} {payment.surname}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-white">
                      {payment.annulment ? "Да" : "Нет"}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-white">
                      {payment.payment_number}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-white">
                      {payment.ls_abon}
                    </td>
                    <td
                      className={`px-4 py-2 whitespace-nowrap text-sm ${getColorClass(
                        payment.payment_status
                      )}`}
                    >
                      {payment.payment_status}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-white">
                      {format(
                        new Date(payment.updated_at),
                        "dd/MM/yyyy hh:mm:ss a"
                      )}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-white">
                      {payment.comment}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-white">
                      {payment.document_number}
                    </td>
                    {userRole === "admin" && (
                      <td className="px-4 py-2 whitespace-nowrap text-sm text-white flex items-center justify-center drop-shadow-md">
                        <button
                          onClick={() => handleOpenDialog(payment)}
                          className="text-blue-400 hover:text-blue-600"
                        >
                          <FaEdit className="text-black" />
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="mt-4 flex justify-between items-center">
          <div className="flex items-center">
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
              disabled={cursorHistory.length <= 1}
            >
              <FaChevronLeft className="mr-2" />
              Назад
            </button>
            <span className="relative inline-flex items-center px-4 py-2 border border-purple-300 bg-white bg-opacity-20 text-sm font-medium text-white">
              Страница {cursorHistory.length}
            </span>
            <button
              onClick={() => handlePageChange("next")}
              className="relative inline-flex items-center px-4 py-2 rounded-r-md border border-purple-300 bg-white bg-opacity-20 text-sm font-medium text-white hover:bg-purple-500 transition-colors duration-300"
              disabled={!cursor}
            >
              Вперед
              <FaChevronRight className="ml-2" />
            </button>
          </nav>
        </div>
      </div>

      <Link
        to="/admin"
        className="mt-8 bg-white text-purple-600 px-6 py-3 rounded-xl font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-purple-100"
      >
        Панель
      </Link>

      {openDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white rounded-lg p-8 max-w-md w-full">
            <h2 className="text-2xl font-bold mb-4">
              {selectedPayment?.id ? "Изменить платеж" : "Новый платеж"}
            </h2>
            {selectedPayment && (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSavePayment();
                }}
              >
                <div className="mb-4">
                  <label
                    className="block text-gray-700 text-sm font-bold mb-2"
                    htmlFor="payment_status"
                  >
                    Статус платежа
                  </label>
                  <input
                    id="payment_status"
                    type="text"
                    value={selectedPayment.payment_status}
                    readOnly
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                <div className="mb-4">
                  <label
                    className="block text-gray-700 text-sm font-bold mb-2"
                    htmlFor="annulment"
                  >
                    Аннулирован
                  </label>
                  <select
                    id="annulment"
                    value={selectedPayment.annulment ? "true" : "false"}
                    onChange={(e) =>
                      setSelectedPayment({
                        ...selectedPayment,
                        annulment: e.target.value === "true",
                      })
                    }
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  >
                    <option value="false">Нет</option>
                    <option value="true">Да</option>
                  </select>
                </div>
                <div className="mb-4">
                  <label
                    className="block text-gray-700 text-sm font-bold mb-2"
                    htmlFor="comment"
                  >
                    Комментарий
                  </label>
                  <textarea
                    id="comment"
                    value={selectedPayment.comment || ""}
                    onChange={(e) =>
                      setSelectedPayment({
                        ...selectedPayment,
                        comment: e.target.value,
                      })
                    }
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                {!selectedPayment.id && (
                  <>
                    <div className="mb-4">
                      <label
                        className="block text-gray-700 text-sm font-bold mb-2"
                        htmlFor="ls_abon"
                      >
                        Лицевой счет
                      </label>
                      <input
                        id="ls_abon"
                        type="text"
                        value={selectedPayment.ls_abon || ""}
                        onChange={(e) =>
                          setSelectedPayment({
                            ...selectedPayment,
                            ls_abon: e.target.value,
                          })
                        }
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                      />
                    </div>
                    <div className="mb-4">
                      <label
                        className="block text-gray-700 text-sm font-bold mb-2"
                        htmlFor="money"
                      >
                        Сумма
                      </label>
                      <input
                        id="money"
                        type="number"
                        value={selectedPayment.money || ""}
                        onChange={(e) =>
                          setSelectedPayment({
                            ...selectedPayment,
                            money: Number(e.target.value),
                          })
                        }
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                      />
                    </div>
                  </>
                )}
                <div className="flex items-center justify-between">
                  <button
                    type="button"
                    onClick={handleCloseDialog}
                    className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                  >
                    Отмена
                  </button>
                  <button
                    type="submit"
                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                  >
                    Сохранить
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {snackbarOpen && (
        <div className="fixed bottom-4 left-4 bg-gray-800 text-white px-6 py-3 rounded-md shadow-lg">
          {snackbarMessage}
        </div>
      )}
    </div>
  );
};

export default PaymentsPage;
