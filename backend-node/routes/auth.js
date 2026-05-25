const express = require('express');
const jwt     = require('jsonwebtoken');
const bcrypt  = require('bcryptjs');
const router  = express.Router();
const db      = require('../db');

const SECRET = 'subgen_secret_key'; 

// POST /api/auth/register - регистрация нового пользователя
router.post('/register', async (req, res) => {
  const { name, login, password } = req.body;

  console.log('📝 Попытка регистрации:', { name, login }); // ЛОГИРОВАНИЕ

  if (!name || !login || !password) {
    return res.status(400).json({ message: 'Заполните все поля' });
  }

  try {
    // Проверяем, существует ли пользователь
    const existing = await db.query('SELECT id FROM users WHERE login = $1', [login]);
    if (existing.rows.length > 0) {
      console.log('❌ Пользователь уже существует:', login); // ЛОГИРОВАНИЕ
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
    console.log('✅ Пользователь создан:', user); // ЛОГИРОВАНИЕ

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
    console.error('❌ Ошибка регистрации:', err); // ЛОГИРОВАНИЕ
    res.status(500).json({ message: err.message });
  }
});

// POST /api/auth/login
router.post('/login', async (req, res) => {
  const { login, password } = req.body;

  console.log('🔐 Попытка входа:', { login, password }); // ЛОГИРОВАНИЕ

  try {
    const result = await db.query('SELECT * FROM users WHERE login = $1', [login]);
    
    console.log('📊 Найдено пользователей:', result.rows.length); // ЛОГИРОВАНИЕ
    
    if (result.rows.length === 0) {
      console.log('❌ Пользователь не найден:', login); // ЛОГИРОВАНИЕ
      return res.status(404).json({ message: 'Пользователь не найден' });
    }

    const user = result.rows[0];
    console.log('👤 Пользователь из БД:', { 
      id: user.id, 
      login: user.login, 
      role: user.role,
      passwordHash: user.password.substring(0, 20) + '...' 
    }); // ЛОГИРОВАНИЕ

    const passwordValid = bcrypt.compareSync(password, user.password);
    console.log('🔑 Пароль валиден:', passwordValid); // ЛОГИРОВАНИЕ
    console.log('🔑 Введённый пароль:', password); // ЛОГИРОВАНИЕ
    console.log('🔑 Хеш из БД:', user.password); // ЛОГИРОВАНИЕ

    const testHash = bcrypt.hashSync(password, 8);
    console.log('🔬 Хеш от введённого пароля:', testHash);
    console.log('🔬 Хеш из БД:', user.password);
    console.log('🔬 Хеши равны?', testHash === user.password);
    
    if (!passwordValid) {
      console.log('❌ Неверный пароль'); // ЛОГИРОВАНИЕ
      return res.status(401).json({ message: 'Неверный пароль' });
    }

    // Генерируем JWT токен
    const token = jwt.sign(
      { id: user.id, role: user.role },
      SECRET,
      { expiresIn: '24h' }
    );

    console.log('✅ Успешный вход, токен создан'); // ЛОГИРОВАНИЕ
    console.log('🎫 Токен:', token.substring(0, 30) + '...'); // ЛОГИРОВАНИЕ

    res.json({
      token,
      user: { id: user.id, name: user.name, login: user.login, role: user.role },
    });
  } catch (err) {
    console.error('❌ Ошибка при входе:', err.message); // ЛОГИРОВАНИЕ
    console.error(err.stack); // ЛОГИРОВАНИЕ
    res.status(500).json({ message: err.message });
  }
});

// GET /api/auth/me — проверка токена
router.get('/me', async (req, res) => {
  const authHeader = req.headers.authorization;
  
  console.log('🔍 Проверка токена, заголовок:', authHeader); // ЛОГИРОВАНИЕ
  
  if (!authHeader) {
    console.log('❌ Нет токена'); // ЛОГИРОВАНИЕ
    return res.status(401).json({ message: 'Нет токена' });
  }

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, SECRET);
    console.log('✅ Токен декодирован:', decoded); // ЛОГИРОВАНИЕ
    
    const result = await db.query('SELECT id, name, login, role FROM users WHERE id = $1', [decoded.id]);
    
    if (result.rows.length === 0) {
      console.log('❌ Пользователь не найден по ID:', decoded.id); // ЛОГИРОВАНИЕ
      return res.status(404).json({ message: 'Пользователь не найден' });
    }

    console.log('✅ Пользователь найден:', result.rows[0]); // ЛОГИРОВАНИЕ
    res.json({ user: result.rows[0] });
  } catch (err) {
    console.log('❌ Токен недействителен:', err.message); // ЛОГИРОВАНИЕ
    res.status(401).json({ message: 'Токен недействителен' });
  }
});

const { requireAuth, requireRole } = require('../middleware/auth');

// Только для админа — получить всех пользователей
router.get('/users', requireAuth, requireRole('admin'), async (req, res) => {
  console.log('📋 Запрос списка пользователей'); // ЛОГИРОВАНИЕ
  try {
    const result = await db.query('SELECT id, name, login, role, created_at FROM users ORDER BY id');
    console.log('✅ Найдено пользователей:', result.rows.length); // ЛОГИРОВАНИЕ
    res.json(result.rows);
  } catch (err) {
    console.error('❌ Ошибка получения пользователей:', err); // ЛОГИРОВАНИЕ
    res.status(500).json({ message: err.message });
  }
});

// Только для админа — изменить роль пользователя
router.patch('/users/:id/role', requireAuth, requireRole('admin'), async (req, res) => {
  const { id } = req.params;
  const { role } = req.body;

  console.log('🔄 Изменение роли пользователя:', { id, role }); // ЛОГИРОВАНИЕ

  if (!['user', 'admin'].includes(role)) {
    return res.status(400).json({ message: 'Некорректная роль' });
  }

  try {
    const result = await db.query(
      'UPDATE users SET role = $1 WHERE id = $2 RETURNING id, name, login, role',
      [role, id]
    );

    if (result.rows.length === 0) {
      console.log('❌ Пользователь не найден:', id); // ЛОГИРОВАНИЕ
      return res.status(404).json({ message: 'Пользователь не найден' });
    }

    console.log('✅ Роль изменена:', result.rows[0]); // ЛОГИРОВАНИЕ
    res.json(result.rows[0]);
  } catch (err) {
    console.error('❌ Ошибка изменения роли:', err); // ЛОГИРОВАНИЕ
    res.status(500).json({ message: err.message });
  }
});

// Только для админа — удалить пользователя
router.delete('/users/:id', requireAuth, requireRole('admin'), async (req, res) => {
  const { id } = req.params;

  console.log('🗑️ Удаление пользователя:', id); // ЛОГИРОВАНИЕ

  try {
    // Проверяем, не удаляет ли админ сам себя
    if (req.user.id === Number(id)) {
      console.log('❌ Попытка удалить самого себя'); // ЛОГИРОВАНИЕ
      return res.status(400).json({ message: 'Нельзя удалить самого себя' });
    }

    await db.query('DELETE FROM users WHERE id = $1', [id]);
    console.log('✅ Пользователь удалён'); // ЛОГИРОВАНИЕ
    res.json({ message: 'Пользователь удалён' });
  } catch (err) {
    console.error('❌ Ошибка удаления:', err); // ЛОГИРОВАНИЕ
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;