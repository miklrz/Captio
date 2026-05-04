import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { sendMessage } from '../redux/dialogsSlice';
import DialogItem from '../components/DialogItem';
import classes from './Dialogs.module.css';

const DIALOGS_DATA = [
  { id: '1', name: 'Lumine',  lastMessage: 'Путешественник, ты уже добрался?', avatar: '🌟' },
  { id: '2', name: 'Aether',  lastMessage: 'Хочу показать тебе новый маршрут.', avatar: '⚔️' },
  { id: '3', name: 'Paimon',  lastMessage: 'Паймон хочет есть!!!',              avatar: '🍖' },
  { id: '4', name: 'Zhongli', text: 'Контракт заключён.',                       avatar: '🪨' },
];

function Dialogs() {
  const { id } = useParams();
  const dispatch = useDispatch();

  // Читаем сообщения из Redux store
  const messages = useSelector(state => state.dialogs.messages[id] || []);

  // Локальный стейт только для поля ввода
  const [inputValue, setInputValue] = useState('');

  const handleSend = () => {
    const trimmed = inputValue.trim();
    if (!trimmed || !id) return;
    dispatch(sendMessage({ dialogId: id, text: trimmed }));
    setInputValue('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  if (id) {
    const dialog = DIALOGS_DATA.find(d => d.id === id);

    return (
      <div className={classes.chat}>
        <div className={classes.chatHeader}>
          <Link to="/dialogs" className={classes.back}>← Назад</Link>
          <span className={classes.chatAvatar}>{dialog?.avatar}</span>
          <span className={classes.chatName}>{dialog?.name}</span>
        </div>

        {/* Список сообщений из Redux */}
        <div className={classes.messages}>
          {messages.map((msg, index) => (
            <div
              key={index}
              className={msg.from === 'me' ? classes.msgOut : classes.msgIn}
            >
              <strong>{msg.from === 'me' ? 'Вы' : dialog?.name}:</strong> {msg.text}
            </div>
          ))}
        </div>

        {/* Поле ввода */}
        <div className={classes.inputArea}>
          <input
            className={classes.input}
            type="text"
            placeholder="Введите сообщение..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button className={classes.sendBtn} onClick={handleSend}>
            Отправить
          </button>
        </div>
      </div>
    );
  }

  // Список диалогов — без изменений
  return (
    <section className={classes.section}>
      <div className={classes.header}>
        <span className={classes.labelNum}>04</span>
        <span>Диалоги</span>
      </div>
      <div className={classes.list}>
        {DIALOGS_DATA.map((dialog) => (
          <DialogItem
            key={dialog.id}
            id={dialog.id}
            name={dialog.name}
            lastMessage={dialog.lastMessage}
            avatar={dialog.avatar}
          />
        ))}
      </div>
    </section>
  );
}

export default Dialogs;