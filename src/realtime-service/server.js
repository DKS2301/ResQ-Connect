/**
 * ResQConnect Realtime Service
 * WebSocket server for real-time updates
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const redis = require('redis');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const promClient = require('prom-client');
const winston = require('winston');

// Configure loggings
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console()
  ]
});

// Prometheus metrics
const register = new promClient.Registry();
promClient.collectDefaultMetrics({ register });

const connectedClients = new promClient.Gauge({
  name: 'realtime_connected_clients',
  help: 'Number of connected WebSocket clients',
  registers: [register]
});

const messagesTotal = new promClient.Counter({
  name: 'realtime_messages_total',
  help: 'Total number of messages sent',
  labelNames: ['type'],
  registers: [register]
});

// Express app setup
const app = express();
const server = http.createServer(app);

// Middleware
app.use(helmet());
app.use(compression());
app.use(cors({
  origin: process.env.CORS_ORIGIN || "*",
  credentials: true
}));
app.use(express.json());

// Socket.IO setup
const io = socketIo(server, {
  cors: {
    origin: process.env.CORS_ORIGIN || "*",
    methods: ["GET", "POST"]
  },
  transports: ['websocket', 'polling']
});

// Redis client for pub/sub
const redisClient = redis.createClient({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379
});

const redisSubscriber = redisClient.duplicate();

// Connect to Redis
(async () => {
  try {
    await redisClient.connect();
    await redisSubscriber.connect();
    logger.info('Connected to Redis');
  } catch (error) {
    logger.error('Redis connection failed:', error);
  }
})();

// Store connected clients by role and location
const connectedUsers = new Map();
const roomSubscriptions = new Map();

// Socket.IO connection handling
io.on('connection', (socket) => {
  logger.info(`Client connected: ${socket.id}`);
  connectedClients.inc();

  // Handle user authentication and room joining
  socket.on('authenticate', (data) => {
    const { userId, role, location, skills } = data;
    
    connectedUsers.set(socket.id, {
      userId,
      role, // coordinator, volunteer, victim
      location,
      skills,
      joinedAt: new Date()
    });

    // Join role-based room
    socket.join(`role:${role}`);
    
    // Join location-based room if location provided
    if (location && location.lat && location.lon) {
      const locationRoom = `location:${Math.floor(location.lat * 100)}_${Math.floor(location.lon * 100)}`;
      socket.join(locationRoom);
    }

    logger.info(`User authenticated: ${userId} as ${role}`);
    socket.emit('authenticated', { status: 'success', userId });
  });

  // Handle location updates
  socket.on('updateLocation', (location) => {
    const user = connectedUsers.get(socket.id);
    if (user) {
      user.location = location;
      
      // Leave old location room and join new one
      const newLocationRoom = `location:${Math.floor(location.lat * 100)}_${Math.floor(location.lon * 100)}`;
      socket.rooms.forEach(room => {
        if (room.startsWith('location:')) {
          socket.leave(room);
        }
      });
      socket.join(newLocationRoom);
      
      logger.info(`Location updated for user: ${user.userId}`);
    }
  });

  // Handle subscription to specific request updates
  socket.on('subscribeToRequest', (requestId) => {
    socket.join(`request:${requestId}`);
    logger.info(`Client subscribed to request: ${requestId}`);
  });

  // Handle subscription to volunteer updates
  socket.on('subscribeToVolunteer', (volunteerId) => {
    socket.join(`volunteer:${volunteerId}`);
    logger.info(`Client subscribed to volunteer: ${volunteerId}`);
  });

  // Handle disconnection
  socket.on('disconnect', () => {
    logger.info(`Client disconnected: ${socket.id}`);
    connectedUsers.delete(socket.id);
    connectedClients.dec();
  });

  // Handle ping for connection health
  socket.on('ping', () => {
    socket.emit('pong');
  });
});

// Redis event subscriptions
const eventChannels = [
  'request.created',
  'request.updated',
  'request.assigned',
  'request.completed',
  'volunteer.available',
  'volunteer.unavailable',
  'match.proposed',
  'match.accepted',
  'match.declined',
  'notification.sent',
  'emergency.alert'
];

eventChannels.forEach(channel => {
  redisSubscriber.subscribe(channel, (message) => {
    try {
      const eventData = JSON.parse(message);
      handleRealtimeEvent(channel, eventData);
    } catch (error) {
      logger.error(`Error parsing event from ${channel}:`, error);
    }
  });
});

// Handle different types of real-time events
function handleRealtimeEvent(eventType, data) {
  logger.info(`Processing event: ${eventType}`, data);
  messagesTotal.inc({ type: eventType });

  switch (eventType) {
    case 'request.created':
      broadcastNewRequest(data);
      break;
    case 'request.updated':
      broadcastRequestUpdate(data);
      break;
    case 'request.assigned':
      broadcastRequestAssignment(data);
      break;
    case 'volunteer.available':
      broadcastVolunteerAvailability(data, true);
      break;
    case 'volunteer.unavailable':
      broadcastVolunteerAvailability(data, false);
      break;
    case 'match.proposed':
      broadcastMatchProposal(data);
      break;
    case 'match.accepted':
      broadcastMatchAcceptance(data);
      break;
    case 'emergency.alert':
      broadcastEmergencyAlert(data);
      break;
    default:
      logger.warn(`Unknown event type: ${eventType}`);
  }
}

function broadcastNewRequest(data) {
  // Notify coordinators
  io.to('role:coordinator').emit('newRequest', data);
  
  // Notify nearby volunteers if location available
  if (data.location) {
    const locationRoom = `location:${Math.floor(data.location.lat * 100)}_${Math.floor(data.location.lon * 100)}`;
    io.to(locationRoom).emit('nearbyRequest', data);
  }
}

function broadcastRequestUpdate(data) {
  // Notify specific request subscribers
  io.to(`request:${data.request_id}`).emit('requestUpdated', data);
  
  // Notify coordinators
  io.to('role:coordinator').emit('requestUpdated', data);
}

function broadcastRequestAssignment(data) {
  // Notify the assigned volunteer
  io.to(`volunteer:${data.volunteer_id}`).emit('requestAssigned', data);
  
  // Notify request subscribers
  io.to(`request:${data.request_id}`).emit('requestAssigned', data);
  
  // Notify coordinators
  io.to('role:coordinator').emit('requestAssigned', data);
}

function broadcastVolunteerAvailability(data, available) {
  // Notify coordinators
  io.to('role:coordinator').emit('volunteerAvailabilityChanged', {
    ...data,
    available
  });
  
  // Notify volunteer subscribers
  io.to(`volunteer:${data.volunteer_id}`).emit('availabilityChanged', {
    available
  });
}

function broadcastMatchProposal(data) {
  // Notify the specific volunteer
  io.to(`volunteer:${data.volunteer_id}`).emit('matchProposed', data);
  
  // Notify coordinators
  io.to('role:coordinator').emit('matchProposed', data);
}

function broadcastMatchAcceptance(data) {
  // Notify request subscribers
  io.to(`request:${data.request_id}`).emit('matchAccepted', data);
  
  // Notify coordinators
  io.to('role:coordinator').emit('matchAccepted', data);
}

function broadcastEmergencyAlert(data) {
  // Broadcast to all connected users
  io.emit('emergencyAlert', data);
}

// REST API endpoints
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'realtime-service',
    connectedClients: connectedUsers.size,
    uptime: process.uptime()
  });
});

app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

app.get('/stats', (req, res) => {
  const stats = {
    connectedClients: connectedUsers.size,
    clientsByRole: {},
    uptime: process.uptime()
  };

  // Count clients by role
  connectedUsers.forEach(user => {
    stats.clientsByRole[user.role] = (stats.clientsByRole[user.role] || 0) + 1;
  });

  res.json(stats);
});

// Broadcast endpoint for external services
app.post('/broadcast', (req, res) => {
  const { event, data, room } = req.body;
  
  if (!event || !data) {
    return res.status(400).json({ error: 'Event and data are required' });
  }

  if (room) {
    io.to(room).emit(event, data);
  } else {
    io.emit(event, data);
  }

  messagesTotal.inc({ type: 'broadcast' });
  logger.info(`Broadcast sent: ${event} to ${room || 'all'}`);
  
  res.json({ status: 'sent', event, room: room || 'all' });
});

// Error handling
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    redisClient.quit();
    redisSubscriber.quit();
    process.exit(0);
  });
});

const PORT = process.env.PORT || 8088;
server.listen(PORT, () => {
  logger.info(`Realtime service listening on port ${PORT}`);
});