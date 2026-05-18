import { configureStore } from '@reduxjs/toolkit';
import dialogsReducer  from './dialogsSlice';
import agreementReducer from './agreementSlice';
import authReducer      from './authSlice';
import tasksReducer from './tasksSlice';

const store = configureStore({
  reducer: {
    dialogs:   dialogsReducer,
    agreement: agreementReducer,
    auth:      authReducer,
    tasks: tasksReducer,
  },
});

export default store;