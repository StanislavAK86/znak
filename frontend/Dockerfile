FROM node:18-alpine as build-stage

WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package*.json ./
RUN npm install

# Принимаем аргумент для API URL
ARG VUE_APP_API_URL
ENV VUE_APP_API_URL=$VUE_APP_API_URL

# Копируем исходники
COPY . .

# Создаем файл .env.production во время сборки
RUN echo "VUE_APP_API_URL=${VUE_APP_API_URL}" > .env.production

# Собираем приложение
RUN npm run build

FROM nginx:stable-alpine
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
