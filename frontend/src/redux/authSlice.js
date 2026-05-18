import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

const API = 'http://localhost:8000/api';

const getApiError = (data, fallback) => data?.detail || data?.message || fallback;

// Thunk — асинхронный вход
export const loginUser = createAsyncThunk(
  'auth/login',
  async ({ login, password }, { rejectWithValue }) => {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ login, password }),
    });
    const data = await res.json();
    if (!res.ok) return rejectWithValue(getApiError(data, 'Ошибка входа'));

    // Сохраняем токен в localStorage
    localStorage.setItem('token', data.token);
    return data; // { token, user }
  }
);

// Thunk — регистрация
export const registerUser = createAsyncThunk(
  'auth/register',
  async ({ name, login, password }, { rejectWithValue }) => {
    const res = await fetch(`${API}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, login, password }),
    });
    const data = await res.json();
    if (!res.ok) return rejectWithValue(getApiError(data, 'Ошибка регистрации'));

    localStorage.setItem('token', data.token);
    return data;
  }
);

// Thunk — восстановление сессии при перезагрузке
export const checkAuth = createAsyncThunk(
  'auth/check',
  async (_, { rejectWithValue }) => {
    const token = localStorage.getItem('token');
    if (!token) return rejectWithValue('Нет токена');

    const res = await fetch(`${API}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    if (!res.ok) return rejectWithValue(getApiError(data, 'Ошибка проверки токена'));
    return { user: data.user, token };
  }
);

// Thunk — получение списка пользователей (только для админа)
export const fetchUsers = createAsyncThunk(
  'auth/fetchUsers',
  async (_, { rejectWithValue }) => {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/auth/users`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    if (!res.ok) return rejectWithValue(getApiError(data, 'Ошибка загрузки пользователей'));
    return data;
  }
);

// Thunk — изменение роли пользователя
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
    const data = await res.json();
    if (!res.ok) return rejectWithValue(getApiError(data, 'Ошибка изменения роли'));
    return data;
  }
);

// Thunk — удаление пользователя
export const deleteUser = createAsyncThunk(
  'auth/deleteUser',
  async (userId, { rejectWithValue }) => {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API}/auth/users/${userId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    if (!res.ok) return rejectWithValue(getApiError(data, 'Ошибка удаления пользователя'));
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
    users: [], // список всех пользователей (для админа)
  },
  reducers: {
    logout(state) {
      state.user = null;
      state.token = null;
      state.users = [];
      localStorage.removeItem('token');
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
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
      // Register
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
      // Check Auth
      .addCase(checkAuth.fulfilled, (state, action) => {
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      // Fetch Users
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.users = action.payload;
      })
      // Update User Role
      .addCase(updateUserRole.fulfilled, (state, action) => {
        const idx = state.users.findIndex(u => u.id === action.payload.id);
        if (idx !== -1) state.users[idx] = action.payload;
      })
      // Delete User
      .addCase(deleteUser.fulfilled, (state, action) => {
        state.users = state.users.filter(u => u.id !== action.payload);
      });
  },
});

export const { logout } = authSlice.actions;
export default authSlice.reducer;
