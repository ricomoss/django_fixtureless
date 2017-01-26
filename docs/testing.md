Testing
=======
Testing is an important part of the maintainability of django-fixtureless.
We focus on building automated testing for the functions/methods
and classes of django-fixtureless. With these efforts, we strive to keep
as close as we can to 100% code coverage in these tested areas.

In django-fixtureless
---------------------

**Warning**
    
    These guides assume that you have already created and activated your
    virtualenv.  If you do not activate your virtualenv, the python
    libraries will be installed globally.

You'll need to ensure you've run the **syncdb** command for the PostgreSQL and MySQL databases.

    $ django-admin.py syncdb --settings=test_django_project.settings.postgres
    $ django-admin.py syncdb --settings=test_django_project.settings.mysql

We use Django's test commands to execute tests on django-fixtureless.
This command should be run from
**django-fixtureless/fixtureless/tests/test_django_project**.

        $ django-admin.py test test_app.tests --settings=test_django_project.settings.sqlite
        $ django-admin.py test test_app.tests --settings=test_django_project.settings.postgres
        $ django-admin.py test test_app.tests --settings=test_django_project.settings.mysql

**Note**

    It may be useful to append the *--failfast* option when running tests.

Notes
-----
We require that tests pass before merging to dev.

MySQL database testing uses Python 2.7 only.  It is possible to use
Python 3.2+ with MySQL-for-Python-3.  But until it is fully supported by
the mysql-python we will not write support for it within the local testing
and development environments.

[MySQL-for-Python-3](https://github.com/davispuh/MySQL-for-Python-3)
