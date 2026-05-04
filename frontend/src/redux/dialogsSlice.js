import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  messages: {
    '1': [{ from: 'Lumine',  text: 'Путешественник, ты уже добрался?' }],
    '2': [{ from: 'Aether',  text: 'Хочу показать тебе новый маршрут.' }],
    '3': [{ from: 'Paimon',  text: 'Паймон хочет есть!!!'              }],
    '4': [{ from: 'Zhongli', text: 'Контракт заключён.'                }],
  },
};

const dialogsSlice = createSlice({
  name: 'dialogs',
  initialState,
  reducers: {
    sendMessage(state, action) {
      const { dialogId, text } = action.payload;
      // Добавляем сообщение пользователя
      state.messages[dialogId].push({ from: 'me', text });
      // Добавляем автоответ
      state.messages[dialogId].push({ from: 'bot', text: 'Сообщение получено!' });
    },
  },
});

export const { sendMessage } = dialogsSlice.actions;
export default dialogsSlice.reducer;