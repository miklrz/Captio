const express = require('express');
const router = express.Router();
const db = require('../db');
const { requireAuth, requireRole } = require('../middleware/auth');

// READ — получить задачи
// Админ видит все задачи, пользователь — только свои
router.get('/', requireAuth, async (req, res) => {
  try {
    let query;
    let params;

    if (req.user.role === 'admin') {
      // Админ видит все задачи со информацией о владельце
      query = `
        SELECT t.*, u.name as owner_name, u.login as owner_login 
        FROM tasks t 
        LEFT JOIN users u ON t.user_id = u.id 
        ORDER BY t.created_at DESC
      `;
      params = [];
    } else {
      // Пользователь видит только свои задачи
      query = 'SELECT * FROM tasks WHERE user_id = $1 ORDER BY created_at DESC';
      params = [req.user.id];
    }

    const result = await db.query(query, params);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// CREATE — создать задачу
router.post('/', requireAuth, async (req, res) => {
  const { title } = req.body;
  if (!title) return res.status(400).json({ message: 'Нужно название задачи' });
  
  try {
    const result = await db.query(
      'INSERT INTO tasks (title, user_id) VALUES ($1, $2) RETURNING *',
      [title, req.user.id]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// UPDATE — изменить задачу
// Пользователь может изменять только свои задачи, админ — любые
router.patch('/:id', requireAuth, async (req, res) => {
  const { id } = req.params;
  const { done } = req.body;
  
  try {
    // Проверяем права
    const checkResult = await db.query('SELECT user_id FROM tasks WHERE id = $1', [id]);
    
    if (checkResult.rows.length === 0) {
      return res.status(404).json({ message: 'Задача не найдена' });
    }

    const taskOwnerId = checkResult.rows[0].user_id;
    
    // Если не админ и не владелец — запрещаем
    if (req.user.role !== 'admin' && req.user.id !== taskOwnerId) {
      return res.status(403).json({ message: 'Нет прав на редактирование этой задачи' });
    }

    const result = await db.query(
      'UPDATE tasks SET done = $1 WHERE id = $2 RETURNING *',
      [done, id]
    );

    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// DELETE — удалить задачу
// Пользователь может удалять только свои задачи, админ — любые
router.delete('/:id', requireAuth, async (req, res) => {
  const { id } = req.params;
  
  try {
    // Проверяем права
    const checkResult = await db.query('SELECT user_id FROM tasks WHERE id = $1', [id]);
    
    if (checkResult.rows.length === 0) {
      return res.status(404).json({ message: 'Задача не найдена' });
    }

    const taskOwnerId = checkResult.rows[0].user_id;
    
    // Если не админ и не владелец — запрещаем
    if (req.user.role !== 'admin' && req.user.id !== taskOwnerId) {
      return res.status(403).json({ message: 'Нет прав на удаление этой задачи' });
    }

    await db.query('DELETE FROM tasks WHERE id = $1', [id]);
    res.json({ message: 'Задача удалена' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;