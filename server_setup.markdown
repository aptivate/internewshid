# How to set up the Internews Humanitation Information Dashboard on a Ubuntu 14.04 environment

This document provides instructions on deploying the [Internews Humanitation Information Dashboard](https://github.com/aptivate/internewshid) on a [Ubuntu 14.04 LTS](http://releases.ubuntu.com/14.04/) environment.

Familiarity with the command line is required.

## Development environment setup

These instructions allow you to setup the HID on a local development machine, based on the desktop edition of Ubuntu 14.04. This setup does not require a web server, as it is for development only and instead uses Django's build in server.

All instructions are to be run in a [terminal](https://help.ubuntu.com/community/UsingTheTerminal), and require a user who can [run sudo](https://help.ubuntu.com/community/RootSudo)

### Pre-requisites

You need to install a MySql server, git, a Python development environment and other system tools:

```sh
    sudo apt-get update
    sudo apt-get install -y mysql-server libmysqlclient-dev git python python-dev python-virtualenv python-pip node-less
```

You will need to know your MySql root password. If you set it up for the first time you will be prompted for the password. If you have set it up previously and forgotten the password you will need to [reset your MySql root password](https://help.ubuntu.com/community/MysqlPasswordReset).

### Fetch and prepare Internews HID application

We will store the internews hid in the user's home directory, under `~/projects/internewshid`. Feel free to place it anywhere else.

First, get a copy of internews hid:

```sh
    mkdir -p ~/projects
    cd ~/projects
    git clone https://github.com/aptivate/internewshid.git
```

This will prompt you for your Github user account. Next you will want to download the application's dependencies and deploy the project locally:

```sh
    cd ~/projects/internewshid/deploy
    ./bootstrap.py
    ./tasks.py deploy:dev
```

This will prompt you for your MySql root password. The final preparation step is to setup a super user who will have access to the administration interface:

```sh
    cd ~/projects/internewshid/django/website
    ./manage.py createsuperuser
```

### Run the tests

To ensure long term maintainability the application contains a number of automated tests. If you want to run the tests you will need to install additional dependencies:

```sh
    sudo apt-get install -y phantomjs
```

The automated tests can then be executing by running:

```sh
    cd ~/projects/internhewshid/django/website
    ./manage.py test
```

### Run the Internews HID application

You can start Django's internal web server by running the following command:

```sh
    cd ~/projects/internhewshid/django/website
    ./manager.py runserver
```

Once this is started, you can point your web browser to `http://localhost:8000` to see the Inteernews HID.

### Notes on the development version

In the development version, the javascript and CSS assets are not compressed, and not combined into a single file. This makes development easier - however it means the page size will be considerably larger than it would be in production.

## Server environment setup

These instructions allow you to setup the HID on a server machine, based on the server edition of Ubuntu 14.04.

All instructions are to be run in a [terminal](https://help.ubuntu.com/community/UsingTheTerminal), and require a user who can [run sudo](https://help.ubuntu.com/community/RootSudo)

### Pre-requisites

You need to install an Apache server, a MySql server, git, a Python development environment and other system tools:

```sh
    sudo apt-get update
    sudo apt-get install -y apache2 libapache2-mod-wsgi mysql-server libmysqlclient-dev git python python-dev python-virtualenv python-pip node-less
```

You will need to know your MySql root password. If you set it up for the first time you will be prompted for the password. If you have set it up previously and forgotten the password you will need to [reset your MySql root password](https://help.ubuntu.com/community/MysqlPasswordReset).

You will also need to know the server hostname - the name that will be used to access the website, eg. `www.example.com`.

### Fetch and prepare Internews HID application

The configuration files expect the application to be under `/var/django/internewshid/current`.

First, get a copy of internews hid:

```sh
    sudo mkdir -p /var/django/internewshid
    cd /var/django/internewshid
    sudo git clone https://github.com/aptivate/internewshid.git current
```

This will prompt you for your Github user account. Next you will want to download the application's dependencies and deploy the project locally:

```sh
    cd /var/django/internewshid/current/deploy
    sudo ./bootstrap.py
    sudo ./tasks.py deploy:production
```

This will prompt you for your MySql root password. Next you need to setup a super user who will have access to the administration interface:

```sh
    cd /var/django/internewshid/current/django/website
    ./manage.py createsuperuser
```

The production version is stricter in terms of security, and you must explicitly allow the host on which you are installing hid by editing `/var/django/internewshid/current/django/website/settings.py` and adding the server host name to the `ALLOWED_HOSTS` configuration. For example you would replace:

```python
    ALLOWED_HOSTS = [
        '.internewshist.aptivate.org',
        'www.internewshid.aptivate.org'
    ]
```

with

```python
    ALLOWED_HOSTS = ['www.example.com']
```

You need to ensure that the web server has write access to the `static` and `upload` folders:

```sh
    chown -R www-data:www-data /var/django/internewshid/current/django/website/static
    chown -R www-data:www-data /var/django/internewshid/current/django/website/static
```
 
Finally you will need to set the Apache configuration file. First copy it in place:

```sh
    sudo cp /var/django/internewshid/current/apache/ubuntu/production.conf /etc/apache/sites-available/internewshid.conf
```

Then edit that file, to set the server name. For example replace the line

```
    ServerName lin-internewshid.aptivate.org
```

With

```
    ServerName www.example.com
```

And if you want to enable all subdomains to direct to this location, you add the following linebelow:

```
    ServerAlias *.example.com
```


Finally, enable the site and restart apache:

``` 
    sudo a2ensite internewshid
    sudo service apache2 restart
```

The site will now be available in your browser at `http://www.example.com`

### Run the tests

To ensure long term maintainability the application contains a number of automated tests. If you want to run the tests you will need to install additional dependencies:

```sh
    sudo apt-get install -y phantomjs
```

The automated tests can then be executing by running:

```sh
    cd /var/django/internhewshid/current/django/website
    sudo ./manage.py test
```
