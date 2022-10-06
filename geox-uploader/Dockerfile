FROM node:16

ENV NUM_WORKERS ${NUM_WORKERS:-1}

WORKDIR /usr/src
COPY package*.json ./
COPY app app/
RUN npm install
COPY tsconfig.json ./

EXPOSE 8080:8080

RUN npm install pm2 -g
RUN npm run tsc

RUN echo Running pm2 with ${NUM_WORKERS} workers

CMD /usr/local/bin/pm2-runtime -i ${NUM_WORKERS} ./app/index.js
