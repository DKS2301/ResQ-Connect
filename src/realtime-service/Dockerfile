FROM node:18-alpine

WORKDIR /app

# Install dependencies first for better caching
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Create non-root user
RUN adduser -D -s /bin/sh appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8088

CMD ["node", "server.js"]