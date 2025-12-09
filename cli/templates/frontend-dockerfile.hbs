FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs && \
    chown -R nextjs:nodejs /app

USER nextjs

# Expose port (internal)
EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Default to dev mode - override in docker-compose for production
CMD ["npm", "run", "dev"]
