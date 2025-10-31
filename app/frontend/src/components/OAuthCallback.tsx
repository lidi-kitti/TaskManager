import React, { useEffect, useState } from 'react';
import { authApi } from '../api/client';

export const OAuthCallback: React.FC = () => {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      const url = new URL(window.location.href);
      const code = url.searchParams.get('code');
      
      if (!code) {
        return;
      }

      try {
        console.log('Обнаружен код авторизации, обмениваем на токен...');
        await authApi.yandexExchangeCode(code);
        console.log('Токен успешно получен и сохранен в localStorage');
        
        // Проверяем, что токен действительно сохранен
        const token = localStorage.getItem('tm_access_token');
        if (!token) {
          throw new Error('Токен не был сохранен в localStorage');
        }
        
        // Очищаем URL от параметра code и перезагружаем страницу
        url.searchParams.delete('code');
        window.history.replaceState({}, document.title, url.pathname || '/');
        
        // Используем reload для гарантированной перезагрузки страницы с новым состоянием
        window.location.reload();
      } catch (e: any) {
        console.error('Ошибка при обмене кода на токен:', e);
        setError(e?.response?.data?.detail || e?.message || 'Произошла ошибка при авторизации');
      }
    };

    handleCallback();
  }, []);

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 max-w-md mx-4">
          <div className="text-red-600 mb-4">
            <strong className="text-lg block mb-2">Ошибка авторизации</strong>
            <p>{error}</p>
          </div>
          <button
            onClick={() => {
              window.location.href = '/';
            }}
            className="w-full px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            Вернуться на главную
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 text-center">
        <div className="inline-block border-4 border-gray-200 border-t-blue-600 rounded-full w-10 h-10 animate-spin mb-4"></div>
        <div className="text-gray-700">Завершение авторизации...</div>
      </div>
    </div>
  );
};

