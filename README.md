# EduFinder

## Development
### Prerequisites
- Python version: `3.6`
- Pip version: `9.0.1` (for Python 3.6) 

Make sure the versions you are using are correct.

```shell script
# setup virtual environment (in project directory)
$ python -m venv venv

# source the virtual environment
$ source venv/bin/activate          # bash
C:\> venv\Scripts\activate.bat      # windows cmd
PS C:\> venv\Scripts\Activate.ps1   # windows powershell

# install dependencies
$ pip install -r requirements.txt
```

### Running the application

Change directory to `/path/to/edufinder/edufinder` and run
```shell script
$ python manage.py migrate
$ python manage.py runserver
```
You should now be able to access the application at [localhost:8000](http://localhost:8000/).

## Production

### Prerequisites
- Install `nginx`
- Install `default-libmysqlclient-dev`

```shell script
# start nginx
$ /etc/init.d/nginx start

# change directory
$ cd /var/www

# clone the repo and change directory
$ git clone https://github.com/sw708e20/edufinder.git
$ cd edufinder

# copy the nginx config to sites-available and make a symlink to sites-enabled
$ cp /var/www/edufinder/nginx/edufinder.conf /etc/nginx/sites-available/
$ ln -s /etc/nginx/sites-available/edufinder.conf /etc/nginx/sites-enabled/edufinder.conf

# make the virtual environment
$ python3.6 -m venv venv

# source the virtual environment
$ source venv/bin/activate

# install dependencies
$ pip3 install -r requirements.txt
$ pip3 install mysqlclient wheel uwsgi

# run uWSGI application
$ uwsgi --uid 33 --gid 33 --ini edufinder_uwsgi.ini
```