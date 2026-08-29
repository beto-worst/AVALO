# Etapa de construcción
FROM node:lts-bullseye-slim as build

WORKDIR /usr/src/app

# Copiar solo los archivos necesarios para la instalación de dependencias
COPY package*.json ./

# Generar el archivo package-lock.json
RUN npm install --package-lock-only

# Instalar dependencias utilizando npm install
RUN npm ci

# Copiar el resto de los archivos después de la instalación de dependencias
COPY . .

# Muestra el contenido del directorio antes de ejecutar npm run build (para depuración)
RUN ls -al

# Ejecuta npm run build
RUN npm run build

# Etapa final
FROM node:lts-bullseye-slim

WORKDIR /usr/src/app

# Copiar solo el archivo package.json y package-lock.json al directorio de trabajo
COPY --from=build /usr/src/app/package*.json ./

# Instalar dependencias en producción (omitir devDependencies)
RUN npm install --only=production

# Instalar Chromium y dependencias necesarias
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD true
RUN apt-get update && apt-get install -yq chromium

# Copiar los archivos construidos
COPY --from=build /usr/src/app/dist ./dist

# Muestra el contenido del directorio después de la copia (para depuración)
RUN ls -al ./dist

# Configurar el comando de inicio
CMD ["node", "dist/main"]

EXPOSE 3001
