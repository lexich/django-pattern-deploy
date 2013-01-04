django-pattern-deploy
=====================

django-pattern-deploy for django-pattern

create django project from [https://github.com/lexich/django-pattern](https://github.com/lexich/django-pattern)

###usage
> pip install -e git+git://github.com/lexich/django-pattern-deploy.git#egg=patterndeploy && django-pattern-deploy.py -n projectname

###requirements

    python 2.7 - check version
    nodejs >= 0.8 - frontend tools
    other dependecies install automatically

###help

Usage: django-pattern-deploy.py [options]

Options:

    -h, --help                          - show this help message and exit
    -n PROJECTNAME, --name=PROJECTNAME  - name of django project
    -t TEMPLATE, --template=TEMPLATE    - template for django project (django-admin.py startproject --template=TEMPLATE
    -d, --debug                         - debug mode
