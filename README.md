bokaru2
=======
Bokaru, for realz this time

Development Environment Setup
-----------------------------
Do this once:

1. Install [VirtualBox](https://www.virtualbox.org/)
2. Install [Vagrant](https://www.vagrantup.com/)
3. Fork the [Git repository](https://github.com/metriclabs/bokaru2)
4. Clone your fork to a directory on your computer
5. Open a console window on your computer.
6. Navigate to the directory where you cloned the Git repository.
7. Run the command: `vagrant up`. Vagrant will do the following **automatically**:
    1. Set up a virtual machine based on Ubuntu
    2. Forward VM port 8000 to host port 8000
    3. Sync current directory with `/home/vagrant/bokaru` directory in VM
    4. Install Postgres, PostGIS and Python
    5. Install Python project dependencies from file `requirements.txt`
    6. Create Postgres user and database `bokaru`
8. Once the vagrant provisioning is complete you can access your VM with this command: `vagrant ssh`
9. **Optional:** Run the following command to bind the python command to version 3 of python:
    1. `echo "alias python=python3" >> ~/.bashrc`
    2. Exit VM using command `exit` and log in again with `vagrant ssh`
10. Set up the environment variable(s) by running the following command(s):
    1. `echo "export DATABASE_URL='postgres://localhost/bokaru?user=bokaru&password=bokaru123'" >> ~/.bashrc`
    4. Exit VM using command `exit` and log in again with `vagrant ssh`
    5. Make sure that variables are set correctly (e.g. `echo $DATABASE_URL` should return the url above)
11. Run the following commands to initialize up the database and collect static files:
    1. Make migrations: `python3 /home/vagrant/bokaru/manage.py makemigrations`
    2. Run migrations: `python3 /home/vagrant/bokaru/manage.py migrate`
    3. Collect static files: `python3 /home/vagrant/bokaru/manage.py collectstatic --noinput`
12. Create Django superuser
    1. Run command `python3 /home/vagrant/bokaru/manage.py createsuperuser`
    2. Enter user's name, email and password (e.g. bokaru, bokaru@bokaru.com, password123)
13. Create product records:
    1. Start the interactive Python shell: `python3 /home/vagrant/bokaru/manage.py shell`
    2. Import the required module: `from chat import test_data`
    3. Run the function: `test_data.make_products()`
    4. **Optional**: create test events by running commands `test_data.make_event_two_groups()` and `test_data.make_event_one_group()`
    5. Run command `exit()` to exit the shell
14. Run the tests
    1. Change directory `cd /home/vagrant/bokaru/`
    2. Run all tests `python3 ./manage.py test`

Done!

Starting the development server
-------------------------------
1. Start the VM: `vagrant up`
2. SSH into the VM: `vagrant ssh`
3. Start the development server `python3 /home/vagrant/bokaru/manage.py runserver 0.0.0.0:8000`
4. Navigate to the [admin panel](http://localhost:8000/admin/) on the host machine
5. NOTE: to start the server using production settings use command `python3 /home/vagrant/bokaru/manage.py runserver 0.0.0.0:8000 --settings=bokaru.settings.prod`

Starting the production server (gunicorn) locally
-------------------------------------------------
1. Start the VM: `vagrant up`
2. SSH into the VM: `vagrant ssh`
3. Navigate to the project directory `cd bokaru`
4. Copy gunicorn service config `sudo cp bokaru/configs/dev/bokaru-gunicorn.conf /etc/init/bokaru-gunicorn.conf`
5. Start the gunicorn service `sudo service bokaru-gunicorn start`
6. Check the status of the gunicorn service: `sudo service bokaru-gunicorn status` and make sure that the socket file `bokaru-gunicorn.sock` exists in home directory
7. If error happens, check the logs in `sudo cat /var/log/upstart/bokaru-gunicorn.log` or `cat logs/bokaru-gunicorn.log`

Vagrant Commands
----------------
`vagrant up`: Start up an existing Vagrant machine or provision a new one in the current directory.

`vagrant ssh`: Login to a Vagrant machine

`vagrant halt`: Shut down a Vagrant machine for use later

`vagrant provision`: Re-provision an existing Vagrant machine.

`vagrant destroy`: Delete a Vagrant machine.

`vagrant global-status`: See the status and installation directory of all Vagrant machines on your computer.

Using Postgres in VM
--------------------
To access postgres in your Vagrant VM follow these steps:

1. Open a console window
2. Login to your Vagrant machine: `vagrant ssh`
3. Run this command to switch to the Postgres user: `sudo su postgres`
4. Run this command to access the sql editor: `psql` or `psql -d bokaru` to connect to database `bokaru`
5. List all extensions: `\dx` (must contain postgis and postgis_topology)
6. Run this command to quit the sql editor: `\q`
7. Run this command to exit the postgres user: `exit`

Using Django's database API
---------------------------
To query the models dynamically use the built-in API:

1. Start the interactive Python shell: `python3 /home/vagrant/bokaru/manage.py shell`
2. Import required models, for example: `from web.models import User`
3. Run queries, for example: `User.objects.all()` or `bob = User.objects.get(displayName = 'bob')`

Changing models
---------------
Do this whenever models are added or modified:

1. Change your models (in models.py).
2. Run `python3 /home/vagrant/bokaru/manage.py makemigrations` to create migrations for those changes.
3. Run `python3 /home/vagrant/bokaru/manage.py migrate` to apply those changes to the database.

Static files
------------
Static files are served by [whitenoise](http://whitenoise.evans.io/en/stable/index.html).

Run the following command to collect and process the static files: `python3 /home/vagrant/bokaru/manage.py collectstatic --noinput`

New python dependencies
-----------------------
When new python dependencies are added, run the following command to install them: `sudo pip3 install --upgrade -r /home/vagrant/bokaru/requirements.txt`

Testing
-------
To run unit test first navigate to the project directory `cd /home/vagrant/bokaru/` and then run all tests with the following command:
`python3 ./manage.py test`

Custom commands
---------------
Here is a list of custom commands that can be called using Django admin:
* Process payments
  * Selects all attendees of events that will start in in the next 24 hours and charges their credit cards
  * Scheduled to run hourly
  * Command: `python3 /home/vagrant/bokaru/manage.py processpayments`
  
Deploy to AWS
-------------
The deployment procedure for AWS server:
* SSH into the server
* Get the latest code from Git: `git pull`
* Make sure the setup files are executable: `chmod +x server_setup.sh`, etc.
* Run the setup command: `./server_setup.sh`
* Run the migrate command: `./server_migrate.sh`
* Start the server: `./server_start.sh`
* Check the status of the service: `sudo systemctl status bokaru-gunicorn`
* Restart service: `sudo systemctl restart bokaru-gunicorn`
