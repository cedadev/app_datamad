# DataMAD2

[User documentation](https://cedadev.github.io/datamad2/)

## Status - Current Developments

See https://docs.google.com/document/d/1Lhu0ALzroLaPMXYi1x3lUFO-UgkpnZ0P8DDgp1ysGv8/edit for details on current work with deployments.

## Editing docs

The documentation is written using Jekyll. A usefull getting started guide
can be found [here](https://jekyllrb.com/docs/step-by-step/01-setup/)

Once you have the pre-requisites installed, navigate to the docs directory and run:

`bundle exec jekyll serve`

This will serve the docs locally and will update as you change the source.

## Set up Guide

Process to set up Datamad2

- Install the datamad2 repository `git clone https://github.com/cedadev/datamad2.git`
   

- Install the required packages found in the requirements.txt file within the datamad repository in a virtual
   environment `pip install -r requirements.txt`
   

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

- Within the terminal, run `python manage.py migrate`.


- With the .csv containing the database, save the file in the same folder as manage.py and run 
`python manage.py import_database --f datamad_csv.csv`
  

- You will want to create a superuser to log in to the site, to do this run `python manage.py createsuperuser`, enter
in a username and password, this will be local, so you can keep it simple.
   

- Within the terminal run `python manage.py rebuild_index`, this process may take some time.





- Lastly, if all was successful, run `python manage.py runserver` and a local server of the site should be running. The
address to which should be given in the terminal. Open the address in your browser to visit the site.
   
