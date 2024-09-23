import React from 'react';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
  return (
    <header className="bg-purple-300 py-4">
      <div className="container mx-auto flex justify-between items-center px-4">
        <Link to="/" className="text-white text-xl font-bold">Home</Link>
        <nav>
          <ul className="flex space-x-4">
            <li>
              <Link to="/activity" className="text-white hover:text-gray-200">Activity Page</Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;
