# tableau_usermanagement
Help manage large scale group assigments in Tableau Server

### Setup
pip install -r requirements.txt


Modify the variables in settings.py or add these environment variables to system:

TABLEAU_SERVER_HOSTNAME - Hostname for your Tableau Server, e.g. https://tableau.mycompany.com

TABLEAU_SERVER_USERNAME - Username for an admin account that can add / subtract from groups in Tableau Server

TABLEAU_USERVER_PASSWORD - Password for an admin account that can add / subtract groups in Tableau Server

tabpg_connstring - pyscopg2 connection string for a readonly account for your Tableau Instance

This can be a Python str, example

"host='192.168.1.1' dbname='workgroup' user='admin' password='password' port=8060"

### Usage

``` python
In [1]: add_to_usergroup('mblanchard','zz_UK');
User mblanchard successfully added to zz_UK

In [2]: remove_from_usergroup('mblanchard','zz_UK');
User mblanchard successfully removed from zz_UK
```
