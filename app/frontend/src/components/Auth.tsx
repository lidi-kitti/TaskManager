import React, { useState } from 'react';
import { authApi } from '../api/client';

export const Auth: React.FC = () => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (mode === 'login') {
        await authApi.login(username, password);
      } else {
        await authApi.register(username, password);
        await authApi.login(username, password);
      }
      window.location.reload();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Ошибка');
    } finally {
      setLoading(false);
    }
  };

  const loginWithYandex = async () => {
    const cfg = await authApi.yandexConfig();
    const url = new URL(cfg.authorize_url);
    url.searchParams.set('response_type', 'code');
    url.searchParams.set('client_id', cfg.client_id);
    url.searchParams.set('redirect_uri', cfg.redirect_uri);
    // Можно добавить state/PKCE по необходимости
    window.location.href = url.toString();
  };

  return (
    <div className="max-w-md mx-auto bg-white shadow rounded p-6">
      <h2 className="text-2xl font-semibold mb-4">
        {mode === 'login' ? 'Вход' : 'Регистрация'}
      </h2>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block text-sm text-gray-700 mb-1">Логин</label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full border rounded px-3 py-2"
            placeholder="username"
            required
            minLength={3}
          />
        </div>
        <div>
          <label className="block text-sm text-gray-700 mb-1">Пароль</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border rounded px-3 py-2"
            placeholder="password"
            required
            minLength={6}
          />
        </div>
        {error && (
          <div className="text-sm text-red-600">{error}</div>
        )}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white rounded py-2 disabled:opacity-50"
        >
          {loading ? 'Загрузка...' : (mode === 'login' ? 'Войти' : 'Зарегистрироваться')}
        </button>
      </form>
      <div className="mt-4">
        <button
          type="button"
          onClick={loginWithYandex}
          className="w-full bg-black text-white rounded py-2"
        >
          Войти через Яндекс
        </button>
      </div>
      <div className="text-sm text-gray-600 mt-4">
        {mode === 'login' ? (
          <button className="underline" onClick={() => setMode('register')}>
            Нет аккаунта? Зарегистрируйтесь
          </button>
        ) : (
          <button className="underline" onClick={() => setMode('login')}>
            Уже есть аккаунт? Войдите
          </button>
        )}
      </div>
    </div>
  );
};
