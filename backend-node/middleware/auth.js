const jwt = require('jsonwebtoken');
const SECRET = 'subgen_secret_key';

// Проверяет что токен валидный
const requireAuth = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ message: 'Нет токена' });

  const token = authHeader.split(' ')[1];
  try {
    req.user = jwt.verify(token, SECRET); // кладём пользователя в запрос
    next();
  } catch {
    res.status(401).json({ message: 'Токен недействителен' });
  }
};

// Проверяет что у пользователя есть нужная роль
const requireRole = (role) => (req, res, next) => {
  if (!req.user.roles.includes(role)) {
    return res.status(403).json({ message: 'Нет доступа — недостаточно прав' });
  }
  next();
};

module.exports = { requireAuth, requireRole };