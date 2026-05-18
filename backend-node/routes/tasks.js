const express = require('express');
const router = express.Router();
const db = require('../db');
const { requireAuth } = require('../middleware/auth');

// READ — получить все задачи
router.get('/',requireAuth, async (req, res) => {
  try {
    const result = await db.query('SELECT * FROM tasks ORDER BY created_at DESC');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// CREATE — создать задачу
router.post('/',requireAuth, async (req, res) => {
  const { title } = req.body;
  if (!title) return res.status(400).json({ message: 'Нужно название задачи' });
  try {
    const result = await db.query(
      'INSERT INTO tasks (title) VALUES ($1) RETURNING *',
      [title]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// UPDATE — пометить задачу выполненной
router.patch('/:id',requireAuth, async (req, res) => {
  const { id } = req.params;
  const { done } = req.body;
  try {
    const result = await db.query(
      'UPDATE tasks SET done = $1 WHERE id = $2 RETURNING *',
      [done, id]
    );
    if (result.rows.length === 0) return res.status(404).json({ message: 'Задача не найдена' });
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// DELETE — удалить задачу
router.delete('/:id',requireAuth, async (req, res) => {
  const { id } = req.params;
  try {
    await db.query('DELETE FROM tasks WHERE id = $1', [id]);
    res.json({ message: 'Задача удалена' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;