import { configureStore } from '@reduxjs/toolkit';
import dialogsReducer from './dialogsSlice';
import agreementReducer from './agreementSlice';

const store = configureStore({
  reducer: {
    dialogs: dialogsReducer,
    agreement: agreementReducer,
  },
});

export default store;