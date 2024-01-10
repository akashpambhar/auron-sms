FROM node:lts-alpine as build

WORKDIR /app
RUN npm cache clean --force
COPY frontend/. /app

RUN npm install -g npm@10.2.1
RUN npm install

ARG configuration=production

RUN npm run ng build --output-path=/app/dist/frontend --configuration=$configuration --verbose

FROM nginx:latest AS ngi

COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html
COPY frontend/nginx.conf  /etc/nginx/conf.d/default.conf.template
COPY frontend/docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
