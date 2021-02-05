# How to run this project
+ *git clone https://github.com/Ander813/fast_api.git*
___
+ Create .env and postgres.env files in conf folder
___

*.env variables*

    CLIENT_ID_VK
    CLIENT_SECRET_VK
    CLIENT_ID_GITHUB
    CLIENT_SECRET_GITHUB
    DB_URI
    SMTP_HOST
    SMTP_PORT
    EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD
    EMAIL_FROM_NAME
    EMAIL_FROM_EMAIL
    PROJECT_NAME
    SERVER_HOST
    REDIS_HOST
___
*postgres.env*

    POSTGRES_USER
    POSTGRES_PASSWORD
    POSTGRES_DB
    
___
+ *docker-compose build*
+ *docker-compose up*
---
## How to make migrations
+ *docker exec -it back aerich init-db*
+ *docker exec -it back migrate*
+ *docker exec -it back upgrade*