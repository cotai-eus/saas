FROM node:20-alpine@sha256:fb4cd12c85ee03686f6af5362a0b0d56d50c58a04632e6c0fb8363f609372293 AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:stable-alpine@sha256:3935cec99c600e0397259f7b26acfdae53883080720e9d3e5d33a5e85a1e7261
RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --ingroup app app && \
    mkdir -p /usr/share/nginx/html && chown app:app /usr/share/nginx/html
COPY --from=build --chown=app:app /app/dist /usr/share/nginx/html
USER app
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]