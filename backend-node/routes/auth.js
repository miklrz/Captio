const express = require('express');
const jwt     = require('jsonwebtoken');
const bcrypt  = require('bcryptjs');
const router  = express.Router();
const db      = require('../db');

const SECRET = 'subgen_secret_key'; 

// POST /api/auth/register - регистрация нового пользователя
router.post('/register', async (req, res) => {
  const { name, login, password } = req.body;

  if (!name || !login || !password) {
    return res.status(400).json({ message: 'Заполните все поля' });
  }

  try {
    // Проверяем, существует ли пользователь
    const existing = await db.query('SELECT id FROM users WHERE login = $1', [login]);
    if (existing.rows.length > 0) {
      return res.status(400).json({ message: 'Пользователь с таким логином уже существует' });
    }

    // Хешируем пароль
    const hashedPassword = bcrypt.hashSync(password, 8);

    // Создаём пользователя
    const result = await db.query(
      'INSERT INTO users (name, login, password, role) VALUES ($1, $2, $3, $4) RETURNING id, name, login, role',
      [name, login, hashedPassword, 'user']
    );

    const user = result.rows[0];

    // Генерируем токен
    const token = jwt.sign(
      { id: user.id, role: user.role },
      SECRET,
      { expiresIn: '24h' }
    );

    res.status(201).json({
      token,
      user: { id: user.id, name: user.name, login: user.login, role: user.role },
    });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// POST /api/auth/login
router.post('/login', async (req, res) => {
  const { login, password } = req.body;

  try {
    const result = await db.query('SELECT * FROM users WHERE login = $1', [login]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Пользователь не найден' });
    }

    const user = result.rows[0];
    const passwordValid = bcrypt.compareSync(password, user.password);
    
    if (!passwordValid) {
      return res.status(401).json({ message: 'Неверный пароль' });
    }

    // Генерируем JWT токен
    const token = jwt.sign(
      { id: user.id, role: user.role },
      SECRET,
      { expiresIn: '24h' }
    );

    res.json({
      token,
      user: { id: user.id, name: user.name, login: user.login, role: user.role },
    });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET /api/auth/me — проверка токена
router.get('/me', async (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ message: 'Нет токена' });

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, SECRET);
    const result = await db.query('SELECT id, name, login, role FROM users WHERE id = $1', [decoded.id]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Пользователь не найден' });
    }

    res.json({ user: result.rows[0] });
  } catch {
    res.status(401).json({ message: 'Токен недействителен' });
  }
});

const { requireAuth, requireRole } = require('../middleware/auth');

// Только для админа — получить всех пользователей
router.get('/users', requireAuth, requireRole('admin'), async (req, res) => {
  try {
    const result = await db.query('SELECT id, name, login, role, created_at FROM users ORDER BY id');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Только для админа — изменить роль пользователя
router.patch('/users/:id/role', requireAuth, requireRole('admin'), async (req, res) => {
  const { id } = req.params;
  const { role } = req.body;

  if (!['user', 'admin'].includes(role)) {
    return res.status(400).json({ message: 'Некорректная роль' });
  }

  try {
    const result = await db.query(
      'UPDATE users SET role = $1 WHERE id = $2 RETURNING id, name, login, role',
      [role, id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Пользователь не найден' });
    }

    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Только для админа — удалить пользователя
router.delete('/users/:id', requireAuth, requireRole('admin'), async (req, res) => {
  const { id } = req.params;

  try {
    // Проверяем, не удаляет ли админ сам себя
    if (req.user.id === Number(id)) {
      return res.status(400).json({ message: 'Нельзя удалить самого себя' });
    }

    await db.query('DELETE FROM users WHERE id = $1', [id]);
    res.json({ message: 'Пользователь удалён' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;