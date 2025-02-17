# DataMAD2

[User documentation](https://cedadev.github.io/datamad2/)

## Status - Current Developments

See https://docs.google.com/document/d/1Lhu0ALzroLaPMXYi1x3lUFO-UgkpnZ0P8DDgp1ysGv8/edit for details on current work with deployments.

## Editing docs

The documentation is written using Jekyll. A useful getting started guide
can be found [here](https://jekyllrb.com/docs/step-by-step/01-setup/)

Once you have the pre-requisites installed, navigate to the docs directory and run:

`bundle exec jekyll serve`

This will serve the docs locally and will update as you change the source.

## Setup guide Python environment
- Clone the datamad2 repository to your local machine in a directory of your choosing `git clone https://github.com/cedadev/datamad2.git`
- Install Python if you haven't already (see datamad2 requirements.txt for Python version)

### Docker
If you have Docker installed (for example via Rancher Desktop) then the simplest install method is to run either Windows:
```
docker build -f .\Dockerfile_debug -t datamad-debug .
```

or Linux (rocky9 tested):
```
docker build -f ./Dockerfile_debug -t datamad-debug .
```

This will install a Rocky9 image with everything needed for Python mysqlclient, the Databank download script and the Django web application to run.

Note one, Rancher Desktop needs to be running for the docker command to work (at least in Windows).
Note two, this does not use any CEDA specific Docker images and should not be used in deployment

### Windows
These instructions may not be extensive
- Download and Install MySQL server (mysql.exe is required for mysqlclient to run)
- Create a Python virtual environment
```
python virtualenv app_datamad
```
- Install the required packages found in the requirements.txt file within the datamad repository into the virtual
   environment you created `pip install -r requirements.txt`

If there are errors such as mysql.exe not found then you might need to add MySQL Server\bin to your user path environment variable. For example for MySQL 8.0 add:
```
C:\Program Files\MySQL\MySQL Server 8.0\bin
```

Note, you might need to check where mysql.exe has been installed on your system as the above might not be the install path for later (or earlier) versions of MySQL server.

Alternatively you could try and use MariaDB instead, but this is untested or Microsoft SQL server, setup an ODBC connection in windows and then change the connection settings in "DataMad_csv_create.py".


### Linux (Rocky9 example)
The install order ensures all dependencies are installed in the correct order.

- Install python
```

dnf install python3 -y
```

Install all dependencies needed for mysqlclient to get access to DataBank through the "DataMad_csv_create.py" script
```
dnf install epel-release -y
crb enable
dnf install python3-devel -y
dnf install mysql-server -y
dnf install pkgconf pkgconf-pkg-config -y
dnf install mysql-devel -y
dnf install gcc -y
pip3 install mysqlclient
```

- Install sqllite support for local database
dnf install sqlite -y

- If somehow not already installed (if you downloaded the datamad repo from a .zip file on the web) then install git to clone ceda-elasticsearch-tools (and others) in in requirements.txt
```
dnf -y install git
```
 - Create Python virtual environment in the directory of your choice, then activate it (depending on how Pyton installed you may need to replace "python3" with "python")
```
python3 virtualenv app_datamad
/bin/activate
```

 - Then install DataMad requirements into the virtual environment
```
pip install --no-cache-dir -r requirements.txt
pip install debugpy
```

## Setup guide DataBank Access
DataBank is a UKRI service containing grant information which is pulled from "The Funding Service" grant application system. The Django application DataMad used a Python script "DataMad_csv_create.py" to generate a .csv file, which Django then uses to import data from DataBank and save it into a local SQLLite file for debugging, or a PostGres database in production.

To use it:
- a local_temp directory must be created
- Within it create a .txt file with the name "sql_alchemy_mysql_conn_string.txt" and place the following into it:
```
mysql+mysqldb://<User>:<Password>@<host>/databank

<User>, <Password> and <host> should be replaced with the DataBank login details.
```

## Setup Guide Django application
Process to set up Datamad2 web application

- In the datamadsite folder you should see a settings_local.py.tmpl file, copy said file and past in the same
location but remove the `.tmpl` extension.
   

- Fill out the settings_local.py template as follows:
```py
SECRET_KEY = '<enter random string>'

...

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack_elasticsearch.elasticsearch7.Elasticsearch7SearchEngine',
        'URL': '',
        'INDEX_NAME': 'datamad2-haystack-test-<name>',
        'TIMEOUT': 5,
        'KWARGS': {
            'headers': {
                'x-api-key': '<api-key>'
            },
            'retry_on_timeout': True,
            'sniffer_timeout': 60,
            'sniff_on_connection_fail': True,
        }
    }
}

...

JIRA_CONSUMER_KEY = 'OAuthKey'
#JIRA_PRIVATE_RSA_KEY_PATH = ''
#JIRA_PRIVATE_RSA_KEY = read(JIRA_PRIVATE_RSA_KEY_PATH)

...
```

In the instructions below you might, depending on your setup, need to replace the string "python" with the string "python3".

If using Docker, then start an interactive Docker shell using `docker run -it -p 8000:8000 datamad-debug` before running the instructions below.

- Within the terminal, run `python manage.py migrate`.

- With the .csv containing the database, save the file in the same folder as manage.py and run 
`python manage.py import_database --file datamad.csv`
  
- You will want to create a superuser to log in to the site, to do this run `python manage.py createsuperuser`, enter
in a username and password, this will be local, so you can keep it simple.
   
- Within the terminal run `python manage.py rebuild_index`, this process may take some time.

- Lastly, if all was successful, run `python manage.py runserver` and a local server of the site should be running. The
address to which should be given in the terminal. Open the address in your browser to visit the site.
   