import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isChecked: false,    // состояние чекбокса
  isAccepted: false,   // подтверждено ли соглашение
};

const agreementSlice = createSlice({
  name: 'agreement',
  initialState,
  reducers: {
    toggleCheckbox(state) {
      state.isChecked = !state.isChecked;
    },
    acceptAgreement(state) {
      if (state.isChecked) {
        state.isAccepted = true;
      }
    },
    resetAgreement(state) {
      state.isChecked = false;
      state.isAccepted = false;
    },
  },
});

export const { toggleCheckbox, acceptAgreement, resetAgreement } = agreementSlice.actions;
export default agreementSlice.reducer;