FROM node:20-slim AS builder

WORKDIR /app

# Сначала копируем только файлы зависимостей (для эффективного кэширования слоев Docker)
COPY package*.json ./

# Устанавливаем библиотеки
RUN npm install

COPY . .

# Собираем production-версию (на выходе получим оптимизированную папку dist/)
RUN npm run build

FROM nginx:alpine

# Копируем результаты сборки React из первого этапа в дефолтную папку Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Копируем кастомный минимальный конфиг Nginx для фронта (чтобы работал React Router)
COPY nginx.frontend.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
