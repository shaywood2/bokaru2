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
    4. Install Postgres and Python
    5. Install Python project dependencies from file `requirements.txt`
    6. Create Postgres user and database
8. Once the vagrant provisioning is complete you can access your VM with this command: `vagrant ssh`
9. **Optional:** Follow these steps to bind the python command to version 3 of python:
    1. Open ~/.bashrc
    2. Add an alias like: `alias python=python3`
    3. Save the file
    4. Restart your console window
10. Set up the environment variable(s) by running the following command(s):
    1. `echo "export DATABASE_URL='postgres://localhost/bokaru?user=bokaru&password=bokaru123'" >> ~/.bashrc`
    2. Exit VM using command `exit` and log in again with `vagrant ssh`
    3. Make sure that variables are set correctly (e.g. `echo $DATABASE_URL` should return the url above)
11. Create and run migrations
    1. `python3 /home/vagrant/bokaru/manage.py makemigrations`
    2. `python3 /home/vagrant/bokaru/manage.py migrate`
    3. `python3 /home/vagrant/bokaru/manage.py collectstatic --noinput`
11. Create Django superuser
    1. Run command `python3 /home/vagrant/bokaru/manage.py createsuperuser`
    2. Enter user's name, email and password (e.g. bokaru, bokaru@bokaru.com, password123)

Done!

Starting the development server
-------------------------------
1. Start the VM: `vagrant up`
2. SSH into the VM: `vagrant ssh`
3. Start the development server `python3 /home/vagrant/bokaru/manage.py runserver 0.0.0.0:8000`
4. Navigate to the [admin panel](http://localhost:8000/admin/) on the host machine

Starting the production server (gunicorn)
-----------------------------------------
1. Start the VM: `vagrant up`
2. SSH into the VM: `vagrant ssh`
3. Navigate to the project directory `cd bokaru`
4. Start the production server by running command `gunicorn -b 0.0.0.0:8000 bokaru.wsgi`
5. Navigate to the [admin panel](http://localhost:8000/admin/) on the host machine

Vagrant Commands
----------------
`vagrant up`: Start up an existing Vagrant machine or provision a new one in the current directory.

`vagrant ssh`: Login to a Vagrant machine

`vagrant halt`: Shut down a Vagrant machine for use later

`vagrant provision`: Re-provision an existing Vagrant machine.

`vagrant destroy`: Delete a Vagrant machine.

`vagrant global-status`: See the status and installation directory of all Vagrant machines on your computer.

Changing models
---------------
Do this whenever models are added or modified:

1. Change your models (in models.py).
2. Run python manage.py makemigrations to create migrations for those changes
3. Run python manage.py migrate to apply those changes to the database.

Static files
------------
Static files are served by [whitenoise](http://whitenoise.evans.io/en/stable/index.html).

Run the following command to collect and process the static files: `python3 /home/vagrant/bokaru/manage.py collectstatic --noinput`