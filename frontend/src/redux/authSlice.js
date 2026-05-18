import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

const API = 'http://localhost:4000/api';

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
    if (!res.ok) return rejectWithValue(data.message);

    // Сохраняем токен в localStorage
    localStorage.setItem('token', data.token);
    return data; // { token, user }
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
    if (!res.ok) return rejectWithValue(data.message);
    return { user: data.user, token };
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user:    null,
    token:   null,
    loading: false,
    error:   null,
  },
  reducers: {
    logout(state) {
      state.user  = null;
      state.token = null;
      localStorage.removeItem('token');
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending,   (state) => { state.loading = true; state.error = null; })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user    = action.payload.user;
        state.token   = action.payload.token;
      })
      .addCase(loginUser.rejected,  (state, action) => {
        state.loading = false;
        state.error   = action.payload;
      })
      .addCase(checkAuth.fulfilled, (state, action) => {
        state.user  = action.payload.user;
        state.token = action.payload.token;
      });
  },
});

export const { logout } = authSlice.actions;
export default authSlice.reducer;