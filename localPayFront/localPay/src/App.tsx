import React, {useEffect} from 'react';
import logo from './logo.svg';
import './App.css';
import Header from './components/Header'
import { Outlet } from 'react-router';
import { useNavigate } from 'react-router-dom';

function App() {
  const navigate = useNavigate();
  
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) navigate('user');
    else navigate('/');
  }, []);

  return (
    <>
      <Outlet />
    </>
  );
}

export default App;
