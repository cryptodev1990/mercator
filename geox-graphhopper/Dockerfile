FROM openjdk:8-jre

COPY config.yml .
RUN wget https://graphhopper.com/public/releases/graphhopper-web-4.0.jar

EXPOSE 8080

# For whatever reason, GraphHopper won't let me switch its port
# So I put it behind a reverse proxy
RUN apt-get update && apt-get install nginx -y
RUN unlink /etc/nginx/sites-enabled/default
COPY reverse-proxy.conf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/reverse-proxy.conf /etc/nginx/sites-enabled/reverse-proxy.conf

COPY start.sh .
CMD ./start.sh
