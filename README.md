# LegalBit
Welcome to LegalBit's Repo

Technologies used are:
* Django
* MariaDB (MySQL Compatible Database)
* Nginx
* Docker
* Bash (For running background tasks)

## Steps for running the proyect in local dev enviroment

1. Install docker or podman (You must modify the ports or the proyect doesn't work)
2. Clone this repo
3. Execute in your terminal :
    1. docker compose build
    2. Could be better if you up the containers each one in this order
        1. ``` docker compose up db -d ```
        2. ``` docker compose up web -d ```
        3. ``` docker compose up nginx -d ```
        4. ``` docker compose up reports -d ```
4. Next you can use the dummy data of Db in the folder MySQL (Use the last schema) or import the copy of DB to your db container by command:
```docker exec -i conainer_id mariadb -u root -p XXXXXXX LegalBit < FILENAME.SQL```

5. Finally the LegalBit Application can be available in localhost (http://localhost) __(if you're using the port 80 and 443 [For SSL connections/HTTPS] the proyect could be doesn't work, you moust modify the ports in the configurations files!!!!)__


## Please don't forget request the Enviroment file for the proyect

__Welcome to team LegalBit__

__*Happy Coding!*__
