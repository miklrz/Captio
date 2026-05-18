const { Pool } = require('pg');

const pool = new Pool({
  host:     'localhost',
  port:     5432,
  database: 'subgen_db',
  user:     'postgres',
  password: 'dascad',
});

module.exports = pool;