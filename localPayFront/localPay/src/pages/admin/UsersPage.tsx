import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import {
  Pagination,
  CircularProgress,
  Snackbar,
  IconButton,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

import { FaChevronLeft, FaChevronRight, FaSignInAlt } from "react-icons/fa";
import { Link } from "react-router-dom";
import EditUserDialog from "../../components/dialogs/EditUserDialog";
import RefillDialog from "../../components/dialogs/RefillDialog";
import WriteOffDialog from "../../components/dialogs/WriteOffDialog";
import UserFilters from "../../components/UserFilters";
import UserTable from "../../components/UserTable";
import { BACKEND_API_BASE_URL } from "../../config";
import useRoleRedirect from "../../hooks/useRoleRedirect";
import { jwtDecode } from "jwt-decode";
import { DecodedToken } from "../../components/DecodedToken";

type User = {
  id: number;
  name: string;
  login: string;
  is_admin: boolean;
  is_active: boolean;
  spent_money: number;
  surname: string;
  date_reg: string;
  access_to_payments: boolean;
  available_balance: number;
  region: string;
  comment: string;
};

const UsersPage: React.FC = () => {
  useRoleRedirect(["admin", "supervisor"]);

  const [users, setUsers] = useState<User[]>([]);
  const [filteredUsers, setFilteredUsers] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [minBalance, setMinBalance] = useState<number | undefined>(undefined);
  const [maxBalance, setMaxBalance] = useState<number | undefined>(undefined);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState<boolean>(false);
  const [refillDialogOpen, setRefillDialogOpen] = useState<boolean>(false);
  const [writeOffDialogOpen, setWriteOffDialogOpen] = useState<boolean>(false);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [perPage, setPerPage] = useState<number>(10);
  const [totalUsers, setTotalUsers] = useState(0);

  const [currentUserRole, setCurrentUserRole] = useState<string>("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token != null) {
      const decodedToken: DecodedToken = jwtDecode(token);
      setCurrentUserRole(decodedToken.role);
    } else {
      setCurrentUserRole("ban");
    }
  }, []);

  const fetchUsers = useCallback(async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No token available");

      const response = await axios.get(`${BACKEND_API_BASE_URL}/users`, {
        params: {
          per_page: 1000000, // Запрашиваем все записи
          min_balance: minBalance,
          max_balance: maxBalance,
        },
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      setUsers(response.data.users);
      setTotalUsers(response.data.total);
      applyFilters(response.data.users);
    } catch (error) {
      console.error("Error fetching users:", error);
    } finally {
      setIsLoading(false);
    }
  }, [minBalance, maxBalance]);

  const applyFilters = useCallback(
    (usersToFilter: User[]) => {
      const filtered = usersToFilter.filter(
        (user) =>
          searchTerm === "" ||
          user.id.toString().includes(searchTerm) ||
          user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          user.surname.toLowerCase().includes(searchTerm.toLowerCase()) ||
          user.login.toLowerCase().includes(searchTerm.toLowerCase()) ||
          user.region.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredUsers(filtered);
      setTotalPages(Math.ceil(filtered.length / perPage));
      setPage(1);
    },
    [searchTerm, perPage]
  );

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  useEffect(() => {
    applyFilters(users);
  }, [applyFilters, users]);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage);
    }
  };

  // const handleDeleteUser = async (userId: number) => {
  //   try {
  //     const token = localStorage.getItem("token");
  //     if (!token) throw new Error("No token available");

  //     await axios.delete(`${BACKEND_API_BASE_URL}/delete_user/${userId}`, {
  //       headers: {
  //         Authorization: `Bearer ${token}`,
  //         "Content-Type": "application/json",
  //       },
  //     });

  //     await fetchUsers();
  //   } catch (error) {
  //     console.error("Error deleting user:", error);
  //   }
  // };

  const handleUpdateUser = async (updatedUser: User) => {
    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No token available");

      await axios.patch(
        `${BACKEND_API_BASE_URL}/update_user/${updatedUser.id}`,
        updatedUser,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      await fetchUsers();
    } catch (error) {
      console.error("Error updating user:", error);
    }
  };

  const handleRefill = async (userId: number, amount: number) => {
    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No token available");

      await axios.patch(
        `${BACKEND_API_BASE_URL}/update_user/${userId}`,
        { refill: amount },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      await fetchUsers();
    } catch (error) {
      console.error("Error refilling balance:", error);
    }
  };

  const handleWriteOff = async (userId: number, amount: number) => {
    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No token available");

      await axios.patch(
        `${BACKEND_API_BASE_URL}/update_user/${userId}`,
        { write_off: amount },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      await fetchUsers();
    } catch (error) {
      console.error("Error writing off balance:", error);
      if (axios.isAxiosError(error) && error.response?.status === 400) {
        setError("Списание не может быть больше потраченного");
      }
    }
  };

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        setError(null);
      }, 10000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const handlePerPageChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setPerPage(Number(event.target.value));
    setPage(1);
  };

  const handleCloseSnackbar = () => {
    setError(null);
  };

  const paginatedUsers = filteredUsers.slice(
    (page - 1) * perPage,
    page * perPage
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 text-white p-4">
      <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-3xl p-8 shadow-2xl">
        <h1 className="text-4xl font-bold mb-6 text-center">
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-purple-100">
            Пользователи LocalPay
          </span>
        </h1>

        <UserFilters
          onSearchChange={(value) => {
            setSearchTerm(value);
            setPage(1);
          }}
          onMinBalanceChange={(value) => {
            setMinBalance(value);
            fetchUsers();
          }}
          onMaxBalanceChange={(value) => {
            setMaxBalance(value);
            fetchUsers();
          }}
        />

        <UserTable
          users={paginatedUsers}
          onUpdateUser={(user) => {
            setSelectedUser(user);
            setEditDialogOpen(true);
          }}
          // onDeleteUser={handleDeleteUser}
          onRefill={(userId) => {
            setSelectedUser(users.find((u) => u.id === userId) || null);
            setRefillDialogOpen(true);
          }}
          onWriteOff={(userId) => {
            setSelectedUser(users.find((u) => u.id === userId) || null);
            setWriteOffDialogOpen(true);
          }}
          userRole={currentUserRole}
        />

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
              onClick={() => handlePageChange(page - 1)}
              className="relative inline-flex items-center px-4 py-2 rounded-l-md border border-purple-300 bg-white bg-opacity-20 text-sm font-medium text-white hover:bg-purple-500 transition-colors duration-300"
              disabled={page === 1}
            >
              <FaChevronLeft className="mr-2" />
              Назад
            </button>

            <span className="relative inline-flex items-center px-4 py-2 border border-purple-300 bg-white bg-opacity-20 text-sm font-medium text-white">
              Страница {page} из {totalPages}
            </span>
            <button
              onClick={() => handlePageChange(page + 1)}
              className="relative inline-flex items-center px-4 py-2 rounded-r-md border border-purple-300 bg-white bg-opacity-20 text-sm font-medium text-white hover:bg-purple-500 transition-colors duration-300"
              disabled={page === totalPages}
            >
              Вперед
              <FaChevronRight className="ml-2" />
            </button>
          </nav>
        </div>

        <nav className="mt-8 flex justify-center space-x-6">
          <Link
            to="/admin"
            className="flex items-center justify-center bg-white text-blue-600 px-6 py-3 rounded-full font-semibold text-lg transition duration-300 ease-in-out transform hover:scale-105 hover:bg-purple-100"
          >
            <FaSignInAlt className="mr-2" />
            Панель
          </Link>
        </nav>
      </div>

      <EditUserDialog
        open={editDialogOpen}
        user={selectedUser}
        onClose={() => setEditDialogOpen(false)}
        onUpdate={handleUpdateUser}
      />
      <RefillDialog
        open={refillDialogOpen}
        onClose={() => setRefillDialogOpen(false)}
        onRefill={(amount) => {
          if (selectedUser) {
            handleRefill(selectedUser.id, amount);
          }
        }}
      />
      <WriteOffDialog
        open={writeOffDialogOpen}
        onClose={() => setWriteOffDialogOpen(false)}
        onWriteOff={(amount) => {
          if (selectedUser) {
            handleWriteOff(selectedUser.id, amount);
          }
        }}
      />

      <Snackbar
        open={!!error}
        autoHideDuration={10000}
        onClose={handleCloseSnackbar}
        message={error}
        action={
          <IconButton
            size="small"
            aria-label="close"
            color="inherit"
            onClick={handleCloseSnackbar}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        }
      />
    </div>
  );
};

export default UsersPage;
