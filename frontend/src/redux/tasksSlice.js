import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

const API = 'http://localhost:4000/api/tasks';

const getHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
  };
};

export const fetchTasks = createAsyncThunk('tasks/fetch', async () => {
  const res = await fetch(API, {
    headers: getHeaders(),
  });
  if (!res.ok) throw new Error('Ошибка загрузки задач');
  return res.json();
});

export const addTask = createAsyncThunk('tasks/add', async (title) => {
  const res = await fetch(API, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error('Ошибка создания задачи');
  return res.json();
});

export const toggleTask = createAsyncThunk('tasks/toggle', async ({ id, done }) => {
  const res = await fetch(`${API}/${id}`, {
    method: 'PATCH',
    headers: getHeaders(),
    body: JSON.stringify({ done }),
  });
  if (!res.ok) throw new Error('Ошибка обновления задачи');
  return res.json();
});

export const deleteTask = createAsyncThunk('tasks/delete', async (id) => {
  const res = await fetch(`${API}/${id}`, {
    method: 'DELETE',
    headers: getHeaders(),
  });
  if (!res.ok) throw new Error('Ошибка удаления задачи');
  return id;
});

const tasksSlice = createSlice({
  name: 'tasks',
  initialState: { list: [], loading: false, error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchTasks.pending, (state) => { 
        state.loading = true; 
        state.error = null;
      })
      .addCase(fetchTasks.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchTasks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(addTask.fulfilled, (state, action) => {
        state.list.unshift(action.payload);
      })
      .addCase(toggleTask.fulfilled, (state, action) => {
        const idx = state.list.findIndex(t => t.id === action.payload.id);
        if (idx !== -1) state.list[idx] = action.payload;
      })
      .addCase(deleteTask.fulfilled, (state, action) => {
        state.list = state.list.filter(t => t.id !== action.payload);
      });
  },
});

export default tasksSlice.reducer;