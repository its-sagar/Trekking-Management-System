# ==========================================
# STAGE 1: Build the Application
# ==========================================
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# ==========================================
# STAGE 2: Serve the Static Assets with Unprivileged Nginx
# ==========================================
FROM nginx:1.27-alpine

ENV NODE_ENV=production

# 1. Create a dedicated non-root user and group named tms-frontend
RUN addgroup -S tms-frontend && adduser -S tms-frontend -G tms-frontend

# 2. Modify Nginx directories so our non-root user has full access to logs and runtime files
RUN chown -R tms-frontend:tms-frontend /usr/share/nginx/html && \
    chown -R tms-frontend:tms-frontend /var/cache/nginx && \
    chown -R tms-frontend:tms-frontend /var/log/nginx && \
    chown -R tms-frontend:tms-frontend /etc/nginx/conf.d

# 3. Re-route the default Nginx PID file location to a directory writable by tms-frontend
RUN touch /var/run/nginx.pid && \
    chown tms-frontend:tms-frontend /var/run/nginx.pid

# 4. Copy the compiled static assets from Stage 1
COPY --from=builder /app/dist /usr/share/nginx/html

# 5. Copy the custom Nginx configuration (Updated for port 8080)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 6. Switch to the non-root user
USER tms-frontend

# 7. Expose an unprivileged port (Linux prevents non-root users from binding to port 80)
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
