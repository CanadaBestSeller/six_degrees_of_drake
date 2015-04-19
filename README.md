# six_degrees_of_drake

A Django Web-app graph that shows the relationships between artists.

## Import Django App
1. Git clone this repo under any django project folder as an app
2. Edit your Django project's configuration files: 
    - in settings.py under INSTALLED-APPS, add this value: 'six_degrees_of_drake'
    - in urls.py under urlpatterns, add this entry: url(r'^six_degrees_of_drake/', include('six_degrees_of_drake.urls'))
3. Populate the database:
    - python manage.py migrate (this initializes all the tables required by django)
    - python manage.py makemigrations six_degrees_of_drake (this initializes all the tables required by six_degrees_of_drake)
