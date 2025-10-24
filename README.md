# my_vulnerable_idor_web

About this web app.
-------------------

This web app allows users to upload files and download them.
But I'm sad to say that the developer forgot to make sure only the owner of the files
can download or modify them. Therefore this application has IDOR vulnerabilities to discover and exploit!.

Happy hacking!~~

How to run on local environment.
--------------------------------

Create a virtual environment.

```
python -m venv venv
source venv/bin/activate
```

Run init_db.py file.

```
python init_db.py
```

Run web app.

```
python app.py
```

Run as docker container.
------------------------

Build the image.

```
docker build -t idor-app .
```

Run the container.

```
docker run -p 8080:8080 idor-app
```

Run the container with extra options. Keep in mind that change the default port requires to
modify exposed ports on dockerfile.

```
docker run -p 8080:8080 idor-app flask run --host=0.0.0.0 --port=8080
```
