import React, { useState, useEffect } from 'react';
import { TaskList } from './components/TaskList';
import { Auth } from './components/Auth';
import { OAuthCallback } from './components/OAuthCallback';
import { authApi } from './api/client';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => !!localStorage.getItem('tm_access_token'));
  const [username, setUsername] = useState(() => localStorage.getItem('tm_username') || 'Пользователь');
  
  // Проверяем, есть ли параметр code в URL (OAuth callback)
  const url = new URL(window.location.href);
  const oauthCode = url.searchParams.get('code');

  // Проверяем аутентификацию при монтировании компонента
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('tm_access_token');
      const user = localStorage.getItem('tm_username') || 'Пользователь';
      setIsAuthenticated(!!token);
      setUsername(user);
    };

    // Проверяем сразу при монтировании
    checkAuth();

    // Слушаем события storage для синхронизации между вкладками
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'tm_access_token' || e.key === 'tm_username') {
        checkAuth();
      }
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const handleLogout = () => {
    authApi.logout();
    localStorage.removeItem('tm_username');
    window.location.reload();
  };

  // Если это OAuth callback, показываем компонент обработки callback
  if (oauthCode) {
    return <OAuthCallback />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">TaskManager</h1>
              <p className="text-gray-600 mt-1">Управление задачами</p>
            </div>
            {isAuthenticated && (
              <div className="flex items-center gap-4">
                <span className="text-gray-700">
                  Привет, <span className="font-semibold">{username}</span>
                </span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                >
                  Выйти
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isAuthenticated ? (
          <TaskList />
        ) : (
          <Auth />
        )}
      </main>

      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-gray-500 text-sm">
            TaskManager © 2024
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;

