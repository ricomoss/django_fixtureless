# Virtual Environment Setup

This guide will help you set up your development environment for fixtureless.

## Linux Installation (Ubuntu/Debian)


**Note**:  The following will assume you are cloning the django_fixtureless sourcecode to **~/django_fixtureless**.  If you are cloning to a different location, you will need to adjust these instructions accordingly.

**Note**:  A dollar sign ($) indicates a terminal prompt, as your user, not root.

1.  Clone the source:

        $ cd ~
        $ git clone git@github.com:ricomoss/django_fixtureless.git

1. Install some required packages:

        $ sudo apt-get install python3.6-dev python3.7-dev python-pip 

1.  Install virtualenv and virtualenvwrapper:

        $ pip install virtualenv
        $ pip install virtualenvwrapper

1.  Add the following to your **~/.bashrc** or **~/.zshrc** file:

        source /usr/local/bin/virtualenvwrapper.sh

1.  Type the following:

        $ source /usr/local/bin/virtualenvwrapper.sh

1.  Create your virtualenv (this will place you into the virtualenv):

        $ mkvirtualenv fixtureless -p /usr/bin/python3

1.  Add the following to the end of the file **~/.virtualenvs/fixtureless/bin/postactivate**:

        export PYTHONPATH=~/django_fixtureless:~/django_fixtureless/fixtureless/tests/test_django_project

1.  Re-activate the virtualenv (leave the virtualenv, and re-enter to gain the new env var):

        $ deactivate fixtureless
        $ workon fixtureless

9.  Install the required Python libraries:

        (fixtureless)$ pip install -r ~/django-fixtureless/requirements.txt
