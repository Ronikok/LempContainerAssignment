# syntax=docker/dockerfile:1
FROM nginx:1.27-alpine

RUN chmod -R g+rwx /var/cache/nginx /var/run /var/log/nginx
# Copy Nginx config and static assets
COPY frontend/nginx.conf /etc/nginx/nginx.conf
COPY frontend/index.html /usr/share/nginx/html/index.html
EXPOSE 80
