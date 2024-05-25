# Running Airflow Application

This guide outlines the steps to stop, rebuild, and start your Airflow application using Docker and Docker Compose.

## Steps

1. **Stop and Remove All Docker Containers:**

   First, ensure that all running Docker containers are stopped and removed. This helps to avoid conflicts and ensures a clean slate for your Airflow application.

   ```sh
   docker rm -f $(docker ps -a -q)

### Bring Down Any Existing Docker Compose Services:

Use the following command to bring down any existing Docker Compose services. This stops and removes the containers defined in your docker-compose.yml file.


  `docker-compose down `

  

### Build the Docker Compose Services:

Next, rebuild the Docker Compose services to ensure that all changes are applied. This step will build the images as specified in your docker-compose.yml.

`docker-compose build`

Start the Docker Compose Services:


### This starts your Airflow application in the background.

```
docker-compose up -d
```



