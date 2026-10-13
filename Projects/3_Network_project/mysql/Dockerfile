# pull mysql image
FROM mysql:8.0
# set environment variables
ENV MYSQL_ROOT_PASSWORD=1234
EnV MYSQL_DATABASE=DockerDB
# copy the sql file to the docker-entrypoint-initdb.d directory
COPY init.sql /docker-entrypoint-initdb.d/
#expose the mysql port ( default is 3306 but we will use 3307 to avoid conflicts with any existing mysql installation on the host machine)
EXPOSE 3307