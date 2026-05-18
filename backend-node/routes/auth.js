const express = require('express');
const jwt     = require('jsonwebtoken');
const bcrypt  = require('bcryptjs');
const router  = express.Router();

const SECRET = 'subgen_secret_key'; 

const users = [
  {
    id: 1,
    name: 'Paimon',
    login: 'paimon',
    password: bcrypt.hashSync('123456', 8),
    roles: ['user'],
    rights: ['can_view_articles'],
  },
  {
    id: 2,
    name: 'Admin',
    login: 'admin',
    password: bcrypt.hashSync('admin123', 8),
    roles: ['admin', 'user'],
    rights: ['can_view_articles', 'can_manage_users'],
  },
];

// POST /api/auth/login
router.post('/login', (req, res) => {
  const { login, password } = req.body;

  const user = users.find(u => u.login === login);
  if (!user) return res.status(404).json({ message: 'Пользователь не найден' });

  const passwordValid = bcrypt.compareSync(password, user.password);
  if (!passwordValid) return res.status(401).json({ message: 'Неверный пароль' });

  // Генерируем JWT токен — это и есть упрощённый аналог PKCE
  const token = jwt.sign(
    { id: user.id, roles: user.roles, rights: user.rights },
    SECRET,
    { expiresIn: '24h' }
  );

  res.json({
    token,
    user: { id: user.id, name: user.name, roles: user.roles, rights: user.rights },
  });
});

// GET /api/auth/me — проверка токена
router.get('/me', (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ message: 'Нет токена' });

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, SECRET);
    const user = users.find(u => u.id === decoded.id);
    res.json({ user: { id: user.id, name: user.name, roles: user.roles, rights: user.rights } });
  } catch {
    res.status(401).json({ message: 'Токен недействителен' });
  }
});

module.exports = router;

const { requireAuth, requireRole } = require('../middleware/auth');

// Только для админа — получить всех пользователей
router.get('/users', requireAuth, requireRole('admin'), (req, res) => {
  const safeUsers = users.map(({ password, ...u }) => u); // пароли не отдаём
  res.json(safeUsers);
});

// Только для админа — изменить роль пользователя
router.patch('/users/:id/role', requireAuth, requireRole('admin'), (req, res) => {
  const { id } = req.params;
  const { roles } = req.body;

  const user = users.find(u => u.id === Number(id));
  if (!user) return res.status(404).json({ message: 'Пользователь не найден' });

  user.roles = roles;
  const { password, ...safeUser } = user;
  res.json(safeUser);
});