# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Install yarn
RUN apk add --no-cache yarn

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Build application
RUN yarn build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

# Install yarn
RUN apk add --no-cache yarn

# Set to production environment
ENV NODE_ENV=production

# Copy necessary files from builder
COPY --from=builder /app/package.json ./
COPY --from=builder /app/yarn.lock ./
COPY --from=builder /app/.next ./.next
# COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.ts ./

# Install production dependencies only
RUN yarn install --production --frozen-lockfile

# Expose the port Next.js runs on
EXPOSE 3000

# Start the application
CMD ["yarn", "start"]