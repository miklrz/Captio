const express = require('express');
const cors    = require('cors');
const authRoutes  = require('./routes/auth');
const tasksRoutes = require('./routes/tasks');

const app = express();

app.use(cors({ origin: 'http://localhost:3000' }));
app.use(express.json());

app.use('/api/auth',  authRoutes);
app.use('/api/tasks', tasksRoutes);

app.listen(4000, () => console.log('Node backend running on port 4000'));