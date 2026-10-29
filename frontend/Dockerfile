# syntax=docker/dockerfile:1
FROM node:22-alpine AS build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM nginx:1.27-alpine

RUN chmod -R g+rwx /var/cache/nginx /var/run /var/log/nginx
COPY frontend/nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/dist/ /usr/share/nginx/html/
EXPOSE 80
