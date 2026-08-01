FROM nginx:1.19.0-alpine
RUN mkdir /tmp/nginx
COPY staticfiles/ ./static
COPY staticfiles/ ./staticfiles
COPY AWS/nginx/default.conf ./etc/nginx/conf.d/default.conf
EXPOSE 80
