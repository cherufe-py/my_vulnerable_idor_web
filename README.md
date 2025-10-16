# my_vulnerable_idor_web
Just a simple web app to show IDOR vulnerabilites.

How to run.

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

About this web app.
This web app allows users to upload files and download them.
But I'm sad to say that the developer forgot to make sure only the owner of the files
can download of modify them. Therefore this application has IDOR vulnerabilities to discover and exploit!.

Happy hacking!`~~