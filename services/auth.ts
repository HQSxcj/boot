import { api } from './api'; // 假设 api.ts 在同级目录

const TOKEN_KEY = 'token';
const ATTEMPTS_KEY = '115_BOT_LOGIN_ATTEMPTS';
const MAX_ATTEMPTS = 5;

export interface LoginResult {
  success: boolean;
  locked: boolean;
  error?: string;
}

export const checkAuth = (): boolean => {
  return !!localStorage.getItem(TOKEN_KEY);
};

// 修正：调用真实的后端 API 验证 2FA
export const verify2FA = async (code: string): Promise<boolean> => {
  try {
    const result = await api.verify2FA(code);
    return result.success;
  } catch (e) {
    return false;
  }
};

export const getFailedAttempts = (): number => {
  return parseInt(localStorage.getItem(ATTEMPTS_KEY) || '0', 10);
};

export const isLocked = (): boolean => {
  return getFailedAttempts() >= MAX_ATTEMPTS;
};

const incrementAttempts = () => {
  const current = getFailedAttempts();
  localStorage.setItem(ATTEMPTS_KEY, (current + 1).toString());
};

const resetAttempts = () => {
  localStorage.removeItem(ATTEMPTS_KEY);
};

export const login = async (username: string, password: string): Promise<LoginResult> => {
  if (isLocked()) {
    return { success: false, locked: true };
  }

  try {
    const resp = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    const payload = await resp.json().catch(() => null);

    if (resp.ok && payload?.success && payload?.data?.token) {
      localStorage.setItem(TOKEN_KEY, payload.data.token);
      resetAttempts();
      return { success: true, locked: false };
    }

    if (resp.status === 423) {
      localStorage.setItem(ATTEMPTS_KEY, MAX_ATTEMPTS.toString());
      return { success: false, locked: true, error: payload?.error || 'locked' };
    }

    incrementAttempts();
    return { success: false, locked: isLocked(), error: payload?.error || 'invalid_credentials' };
  } catch {
    return { success: false, locked: false, error: 'network' };
  }
};

export const logout = () => {
  const token = localStorage.getItem(TOKEN_KEY);
  localStorage.removeItem(TOKEN_KEY);
  
  // 尝试调用后端注销
  if (token) {
    fetch('/api/auth/logout', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    }).catch(() => {});
  }
};
