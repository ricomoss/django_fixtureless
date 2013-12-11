==========================
Virtual Environment Setup
==========================

This guide will help you set up your development environment for
django-fixtureless.

Linux Installation (Ubuntu/Debian)
==================================

By following these steps, you can easily have a working installation of the
django-fixtureless development environment.

.. note::

   The following will assume you are cloning the django-fixtureless sourcecode
   to **~/django-fixtureless**.  If you are cloning to a different location,
   you will need to adjust these instructions accordingly.

.. note::

   A dollar sign ($) indicates a terminal prompt, as your user, not root.

1.  Clone the source::

        $ cd ~
        $ git clone git@github.com:ricomoss/django-fixtureless.git

2. Install some required packages::

        $ sudo apt-get install python python-dev python-pip

3.  Install virtualenv and virtualenvwrapper::

        $ pip install virtualenv
        $ pip install virtualenvwrapper

4.  Add the following to your **~/.bashrc** or **~/.zshrc** file::

        source /usr/local/bin/virtualenvwrapper.sh

5.  Type the following::

        $ source /usr/local/bin/virtualenvwrapper.sh

6.  Create your virtualenv (for Python 2.7 and Python 3.3, respectively)::

        $ mkvirtualenv django-fixtureless
        $ mkvirtualenv django-fixtureless -p /usr/bin/python3


.. note::

    If you are using any virtualenv version prior to 1.10 it is strongly
    recommended that you upgrade to the most recent version (especially
    if you want to use Python 3).

7.  Add the following to the end of the file
    **~/.virtualenvs/django-fixtureless/bin/postactivate**::

        export DJANGO_SETTINGS_MODULE=test_django_project.settings
        export PYTHONPATH=$PYTHONPATH:~/django-fixtureless/fixtureless/tests/test_django_project/test_django_project/:~/django-fixtureless/fixtureless/

8.  Activate the virtualenv::

        $ workon django-fixtureless

9.  Install the required Python libraries::

        (django-fixtureless)$ pip install -r ~/django-fixtureless/requirements.pip
