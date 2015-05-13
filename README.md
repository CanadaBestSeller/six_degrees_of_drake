# six_degrees_of_drake

A Django Web-app graph that shows the relationships between artists.

## Import Django App
1. Git clone this repo under any django project folder as an app
2. Edit your Django project's configuration files: 
    - in settings.py under INSTALLED-APPS, add this value: ```'six_degrees_of_drake'```
    - in urls.py under urlpatterns, add this entry: ```url(r'^six_degrees_of_drake/', include('six_degrees_of_drake.urls'))```
3. Populate the database:
    - ```python manage.py migrate``` (this initializes all the tables required by django)
    - ```python manage.py makemigrations six_degrees_of_drake``` (this initializes all the tables required by six_degrees_of_drake)

## Deployment via mod_wsgi
1. Apache2 configuration
    - Append the following to apache2.conf:

        ```
        # Djago configuration
        WSGIScriptAlias / /home/azureuser/public_html/sourcedave.cloudapp.net/david/david/wsgi.py
        WSGIPythonPath /home/azureuser/public_html/sourcedave.cloudapp.net/david

        <Directory /home/azureuser/public_html/sourcedave.cloudapp.net/david/david>
            <Files wsgi.py>
            Require all granted
            </Files>
        </Directory>
        ```
        
2. Additional Virtual host configuration for apache
    - Under ```/etc/apache2/sites-available```, create ```sourcedave.cloudapp.net.conf``` NOTE: conf file MUST end in .conf
    - Contents of the conf file should be:

        ```
        <VirtualHost *:80>
            ServerName sourcedave.cloudapp.net
            WSGIScriptAlias / /home/azureuser/public_html/sourcedave.cloudapp.net/david/david/wsgi.py
        </VirtualHost>
        ```
        
3. wsgi.py
    - The default wsgi.py provided by ```django-admin startproject [project_name]``` already works, it only needs the sys path of the website:
        - Append the following to wsgi.py:

            ```
            import sys
            sys.path.append('/home/azureuser/public_html/sourcedave.cloudapp.net/')
            ```

4. Static files
    - Make sure client requests to server is aliased properly. Append to apache2.conf:

        ```
        Alias /media/ /home/azureuser/public_html/sourcedave.cloudapp.net/media/
        Alias /static/ /home/azureuser/public_html/sourcedave.cloudapp.net/static/
        ```

    - Make sure client can access aliased directories. Append to apache2.conf:

        ```
        <Directory /home/azureuser/public_html/sourcedave.cloudapp.net/media>
            Require all granted
        </Directory>

        <Directory /home/azureuser/public_html/sourcedave.cloudapp.net/static>
            Require all granted
        </Directory>
        ```

    - Now we have to populate the static folder with content copied from django.
        - let django know the location of the static folder to populate.
            - Append to settings.py:```STATIC_ROOT = '/home/azureuser/public_html/sourcedave.cloudapp.net/static/'```
            - To copy the static files over, run```python manage.py collectstatic``` NOTE: this has to be done every time static files change.
5. Error logs
    - the apache error log are located @ ```/var/log/apache2/error.log```
