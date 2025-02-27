# **Mustard Imports** 
## To be able to clone the repo .
1st activate te virtual env using this command
```bash
\env\Scripts\acitivate
```
if there is no virtual env create one using 
```bash
python -m venv venvm 
```
then pip install requirements from the requirements.txt and you'll be all good to start .
using 
```bash
pip install dotenv pillow django psycopg2
```
then make migrations while in the root directory where manage.py is found 
```bash
python manage.py makemigrations
python manage.py migrate 
```
To create super user
```bash
python manage.py createsuperuser 
```
To runserver
```bash
python manage.py runserver
```