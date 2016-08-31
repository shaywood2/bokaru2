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
7. Run the command: `vagrant up`. Vagrant will do the following automatically:
    1. Set up a virtual machine based on Ubuntu
    2. Forward VM port 8000 to host port 8000
    3. Sync current directory with `/home/vagrant/bokaru` directory in VM
    4. Install Postgres and Python
    5. Install Python project dependencies from file `requirements.txt`
    6. Create Postgres user and database
    7. Run migrations (initialize the project's database)
8. Once the vagrant provisioning is complete you can access your VM with this command: `vagrant ssh`
9. **Optional:** Follow these steps to bind the python command to version 3 of python:
    1. Open ~/.bashrc
    2. Add an alias like: `alias python=python3`
    3. Save the file
    4. Restart your console window
10. Create Django superuser
    1. In VM's command line navigate to directory `/home/vagrant/bokaru/mysite`
    2. Run command `python3 manage.py createsuperuser`
    3. Enter user's name, email and password
11. Start the development server `python3 manage.py runserver 0.0.0.0:8000`
12. Navigate to [admin panel](http://localhost:8000/admin/) on the host machine

Done!

Changing models
---------------
Do this whenever models are added or modified:

- Change your models (in models.py).
- Run python manage.py makemigrations to create migrations for those changes
- Run python manage.py migrate to apply those changes to the database.
