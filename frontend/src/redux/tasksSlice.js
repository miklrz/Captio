import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

const API = 'http://localhost:4000/api/tasks';

export const fetchTasks  = createAsyncThunk('tasks/fetch',  async () => {
  const res = await fetch(API);
  return res.json();
});

export const addTask     = createAsyncThunk('tasks/add',    async (title) => {
  const res = await fetch(API, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  return res.json();
});

export const toggleTask  = createAsyncThunk('tasks/toggle', async ({ id, done }) => {
  const res = await fetch(`${API}/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ done }),
  });
  return res.json();
});

export const deleteTask  = createAsyncThunk('tasks/delete', async (id) => {
  await fetch(`${API}/${id}`, { method: 'DELETE' });
  return id;
});

const tasksSlice = createSlice({
  name: 'tasks',
  initialState: { list: [], loading: false },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchTasks.pending,   (state) => { state.loading = true; })
      .addCase(fetchTasks.fulfilled, (state, action) => {
        state.loading = false;
        state.list    = action.payload;
      })
      .addCase(addTask.fulfilled,    (state, action) => {
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