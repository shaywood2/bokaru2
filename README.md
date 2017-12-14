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
    1. Set up a virtual machine based on Ubuntu 16.4 (Xenial)
    2. Forward VM ports
        1. 80 (Nginx reverse proxy)
        2. 8080 (Gunicorn application server)
        3. 8000 (Django test server)
        4. 5432 (Postgres)
    3. Sync current directory with `/usr/local/bokaru/` directory in VM
    4. Install Postgres, PostGIS, Python, Gunicorn and Nginx
    5. Install Python project dependencies from files `requirement/common.txt` and `requirement/dev.txt`
    6. Create Postgres user (*bokaru/bokaru123*) and database `bokaru`
    7. Create output folders for logs and uploaded files in the root folder
    8. Run migrations and collect static files
    9. Create a superuser (*admin/admin*)
    10. Create 3 products required for event creation
    11. Set up Gunicorn application server
    12. Set up Nginx reverse proxy
8. Once the vagrant provisioning is complete you can access your VM with this command: `vagrant ssh`
9. **Optional:** Run the following command to bind the python command to version 3 of python:
    1. `echo "alias python=python3" >> ~/.bashrc`
    2. Exit VM using command `exit` and log in again with `vagrant ssh`
10. **Optional:** Create test data:
    1. Start the interactive Python shell: `python3 /usr/local/bokaru/manage.py shell`
    2. Import the required module: `from chat import test_data`
    3. Create test events by running commands `test_data.make_event_two_groups()` and `test_data.make_event_one_group()`
    4. Run command `exit()` to exit the shell
11. **Optional:** Run the tests:
    1. Change directory `cd /usr/local/bokaru/`
    2. Run all tests `python3 ./manage.py test`

Done!

Using the production setup locally
----------------------------------
1. Navigate to the [website](http://localhost/) on the host machine, the servers should be running
2. If error happens, check the logs in folder `/usr/local/bokaru/logs/`

Starting the development server
-------------------------------
1. Start the development server `python3 /usr/local/bokaru/manage.py runserver 0.0.0.0:8000`
2. Navigate to the [website](http://localhost:8000/) on the host machine
3. NOTE: to start the server using production settings use command `python3 /home/vagrant/bokaru/manage.py runserver 0.0.0.0:8000 --settings=bokaru.settings.prod`

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

1. Start the interactive Python shell: `python3 /usr/local/bokaru/manage.py shell`
2. Import required models, for example: `from web.models import User`
3. Run queries, for example: `User.objects.all()` or `bob = User.objects.get(displayName = 'bob')`

Changing models
---------------
Do this whenever models are added or modified:

1. Change your models (in models.py).
2. Run `python3 /usr/local/bokaru/manage.py makemigrations` to create migrations for those changes.
3. Run `python3 /usr/local/bokaru/manage.py migrate` to apply those changes to the database.

Static files
------------
Do this after adding new static files:

Run the following command to collect and process the static files: `python3 /usr/local/bokaru/manage.py collectstatic --noinput`

New python dependencies
-----------------------
When new python dependencies are added, run the following command to install them: `sudo pip3 install --upgrade -r /usr/local/bokaru/requirements.txt`

Testing
-------
To run unit test first navigate to the project directory `cd /usr/local/bokaru/` and then run all tests with the following command:
`python3 ./manage.py test`

Custom commands
---------------
Here is a list of custom commands that can be called using Django admin:
* Process payments
  * Selects all attendees of events that will start in in the next 24 hours and charges their credit cards
  * Scheduled to run hourly
  * Command: `python3 /usr/local/bokaru/manage.py processpayments`
  
Deploy to AWS
-------------
The deployment procedure for AWS server:
1. Spin up a server instance
2. SSH into the new server
3. Run the following commands:
  1. `sudo mkdir -p /usr/local/bokaru/`
  2. `sudo chown -R ubuntu /usr/local/bokaru/`
  3. `cd /usr/local/bokaru/`
  4. `git clone https://github.com/dpyryesk/bokaru2.git .`
  5. `nano configs/prod/env.json` and update the production keys
  6. `chmod +x server_setup.sh`
  7. `./server_setup.sh`


Create Postgis extension in the database
`psql -h bokaru-db.ccmerekzzbun.ca-central-1.rds.amazonaws.com -p 5432 -U bokaru`
`CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;`
