FROM node:16

WORKDIR /usr/src
COPY package*.json ./
COPY app app/
RUN npm install
COPY tsconfig.json ./

EXPOSE 8080:8080

RUN npm install pm2 -g
RUN npm run tsc
CMD ["pm2-runtime", "-i", "8", "./app/index.js"]
