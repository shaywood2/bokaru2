# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  # Ubuntu 16.4
  config.vm.box = "v0rtex/xenial64"

  # Forward ports
  config.vm.network "forwarded_port", guest: 80, host: 80     # Nginx
  config.vm.network "forwarded_port", guest: 8080, host: 8080 # Web server
  config.vm.network "forwarded_port", guest: 8000, host: 8000 # Test server
  config.vm.network "forwarded_port", guest: 5432, host: 5432 # Postgres

  config.vm.synced_folder ".", "/usr/local/bokaru"

  config.ssh.forward_agent = true

  # Set username and password
  config.ssh.username = 'vagrant'
  config.ssh.password = 'vagrant'

  # Provider-specific configuration
  config.vm.provider "virtualbox" do |v|
    v.memory = 4096
    v.cpus = 2
  end

  # Enable provisioning with a shell script
  config.vm.provision "shell", inline: <<-SHELL
    # Install updates
    sudo apt-get update

    # Install dependencies
    sudo apt-get install -y supervisor
    sudo apt-get install -y nginx
    sudo apt-get install -y python3-pip
    sudo apt-get install -y memcached
    sudo apt-get install -y libmemcached-dev
    sudo apt-get install -y postgis postgresql-9.5-postgis-2.2
    sudo apt-get build-dep -y psycopg2
    sudo apt-get install -y libjpeg8
    sudo apt-get install -y libjpeg-dev
    sudo apt-get install -y zlib1g
    sudo apt-get install -y build-essential libssl-dev libffi-dev python-dev

    # Install Python dependencies
    sudo pip3 install -r /usr/local/bokaru/requirements/common.txt
    sudo pip3 install -r /usr/local/bokaru/requirements/dev.txt

    # Create Postgres user and DB, install extensions
    sudo -u postgres psql -c "CREATE ROLE bokaru WITH LOGIN SUPERUSER PASSWORD 'bokaru123'"
    sudo -u postgres psql -c "CREATE DATABASE bokaru WITH OWNER bokaru"
    sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;" bokaru

    # Create upload folders
    mkdir -p /usr/local/bokaru/www/uploads/event-photos
    mkdir -p /usr/local/bokaru/www/uploads/user-photos

    # Migrations and static files
    python3 /usr/local/bokaru/manage.py makemigrations
    python3 /usr/local/bokaru/manage.py migrate
    python3 /usr/local/bokaru/manage.py collectstatic --noinput

    # Create superuser (admin/admin)
    python3 /usr/local/bokaru/manage.py createadmin

    # Create products
    python3 /usr/local/bokaru/manage.py createproducts

    # Copy gunicorn configs
    sudo cp /usr/local/bokaru/configs/dev/gunicorn_bokaru.sh /usr/local/bin/gunicorn_bokaru.sh
    sudo chmod +x /usr/local/bin/gunicorn_bokaru.sh
    sudo cp /usr/local/bokaru/configs/dev/supervisor_gunicorn_bokaru.conf /etc/supervisor/conf.d
    sudo supervisorctl reread
    sudo supervisorctl update

    # Copy Nginx configs
    sudo cp /usr/local/bokaru/configs/dev/nginx.conf /etc/nginx/nginx.conf
    sudo cp /usr/local/bokaru/configs/dev/nginx_bokaru.conf /etc/nginx/sites-available/
    sudo ln -s /etc/nginx/sites-available/nginx_bokaru.conf /etc/nginx/sites-enabled/
    sudo rm /etc/nginx/sites-enabled/default
    sudo systemctl restart nginx

    SHELL
end
