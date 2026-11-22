FROM node:18-alpine AS build-stage

WORKDIR /app

COPY package*.json ./
RUN npm install

# Принимаем аргумент и делаем его доступным для Vue CLI
ARG VUE_APP_API_URL
ENV VUE_APP_API_URL=$VUE_APP_API_URL

COPY . .

# Эту строку НУЖНО УДАЛИТЬ:
# RUN echo "VUE_APP_API_URL=${VUE_APP_API_URL}" > .env.production

RUN npm run build

FROM nginx:stable-alpine
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80