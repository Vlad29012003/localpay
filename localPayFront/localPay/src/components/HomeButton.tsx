import React from 'react';
import { Link } from 'react-router-dom';

const HomeButton: React.FC = () => {
  return (
    <div className="mt-8 flex justify-center">
      <Link
        to="/"
        className="bg-blue-500 text-white py-2 px-4 rounded transition duration-300 ease-in-out transform hover:bg-green-700 hover:shadow-lg hover:-translate-y-1"
      >
        На главную
      </Link>
    </div>
  );
};

export default HomeButton;
