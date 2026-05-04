import React from 'react';
import { Link } from 'react-router-dom';
import classes from './DialogItem.module.css';

// Компонент принимает props: id, name, lastMessage, avatar
const DialogItem = (props) => {
  const path = "/dialogs/" + props.id;

  return (
    <Link to={path} className={classes.item}>
      <div className={classes.avatar}>{props.avatar}</div>
      <div className={classes.info}>
        <span className={classes.name}>{props.name}</span>
        <span className={classes.preview}>{props.lastMessage}</span>
      </div>
    </Link>
  );
};

export default DialogItem;
