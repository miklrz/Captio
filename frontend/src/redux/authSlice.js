import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { API_ROOT } from '../config';

const API = API_ROOT;

const parseApiError = async (res, fallback) => {
  const data = await res.json().catch(() => ({}));
  if (Array.isArray(data?.detail)) {
    return data.detail.map((item) => item.msg || item.detail || String(item)).join('; ');
  }
  return data?.detail || data?.message || fallback;
};

const logApiError = (operation, res, message) => {
  console.error(`[Captio API] ${operation} failed`, {
    status: res.status,
    statusText: res.statusText,
    url: res.url,
    message,
  });
};

export const loginUser = createAsyncThunk(
  'auth/login',
  async ({ login, password }, { rejectWithValue }) => {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ login: login.trim(), password }),
    });
    if (!res.ok) {
      const message = await parseApiError(res, 'Ошибка входа');
      logApiError('login', res, message);
      return rejectWithValue(message);
    }
    const data = await res.json();
    localStorage.setItem('token', data.token);
    return data;
  }
);

export const registerUser = createAsyncThunk(
  'auth/register',
  async ({ name, login, password }, { rejectWithValue }) => {
    const res = await fetch(`${API}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name.trim(),
        login: login.trim(),
        password,
      }),
    });
    if (!res.ok) {
      const message = await parseApiError(res, 'Ошибка регистрации');
      logApiError('register', res, message);
      return rejectWithValue(message);
    }
    const data = await res.json();
    localStorage.setItem('token', data.token);
    return data;
  }
);

export const checkAuth = createAsyncThunk(
  'auth/check',
  async (_, { rejectWithValue }) => {
    const token = localStorage.getItem('token');
    if (!token) return rejectWithValue('Нет токена');

    const res = await fetch(`${API}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      const message = await parseApiError(res, 'Ошибка проверки токена');
      logApiError('checkAuth', res, message);
      localStorage.removeItem('token');
      return rejectWithValue(message);
    }
    const data = await res.json();
    return { user: data.user, token };
  }
);

export const fetchUsers = createAsyncThunk(
  'auth/fetchUsers',
  async (_, { rejectWithValue }) => {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/auth/users`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      const message = await parseApiError(res, 'Ошибка загрузки пользователей');
      logApiError('fetchUsers', res, message);
      return rejectWithValue(message);
    }
    return res.json();
  }
);

export const updateUserRole = createAsyncThunk(
  'auth/updateUserRole',
  async ({ userId, role }, { rejectWithValue }) => {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/auth/users/${userId}/role`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ role }),
    });
    if (!res.ok) {
      const message = await parseApiError(res, 'Ошибка изменения роли');
      logApiError('updateUserRole', res, message);
      return rejectWithValue(message);
    }
    return res.json();
  }
);

export const deleteUser = createAsyncThunk(
  'auth/deleteUser',
  async (userId, { rejectWithValue }) => {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/auth/users/${userId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      const message = await parseApiError(res, 'Ошибка удаления пользователя');
      logApiError('deleteUser', res, message);
      return rejectWithValue(message);
    }
    return userId;
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    token: null,
    loading: false,
    error: null,
    users: [],
  },
  reducers: {
    logout(state) {
      state.user = null;
      state.token = null;
      state.users = [];
      localStorage.removeItem('token');
    },
    clearAuthError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(registerUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(checkAuth.fulfilled, (state, action) => {
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.users = action.payload;
      })
      .addCase(updateUserRole.fulfilled, (state, action) => {
        const idx = state.users.findIndex((u) => u.id === action.payload.id);
        if (idx !== -1) state.users[idx] = action.payload;
      })
      .addCase(deleteUser.fulfilled, (state, action) => {
        state.users = state.users.filter((u) => u.id !== action.payload);
      });
  },
});

export const { logout, clearAuthError } = authSlice.actions;
export default authSlice.reducer;
