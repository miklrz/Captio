\c subgen_db

\dt

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  login VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tasks (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  done BOOLEAN DEFAULT FALSE,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT NOW()
);

\d tasks


INSERT INTO users (name, login, password, role) VALUES
  ('Paimon', 'paimon', '$2b$08$6Ey4Vkx/kXYRGJVK9FRHguw1Ky86.jGtEnZUl1jwj7UKHQsB/OgGO', 'user'),
  ('Admin', 'admin', '$2b$08$caDARljLcT5PPs6GkvTWU.YgtVjhlJ31X/WQK7kq3usQYPqTuVqMe', 'admin');

SELECT id, name, login, role FROM users;

\q