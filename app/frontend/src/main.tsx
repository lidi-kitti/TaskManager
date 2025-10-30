import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { authApi } from './api/client';

// Если пришёл код от Яндекс OAuth, обменяем его на токен и очистим URL
async function bootstrap() {
  const url = new URL(window.location.href);
  const code = url.searchParams.get('code');
  if (code) {
    try {
      await authApi.yandexExchangeCode(code);
      url.searchParams.delete('code');
      window.history.replaceState({}, document.title, url.toString());
    } catch (e) {
      // оставим URL как есть в случае ошибки
    }
  }
}

await bootstrap();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

