Testing
=======
Testing is an important part of the maintainability of django-fixtureless.
We focus on building automated testing for the functions/methods
and classes of django-fixtureless. With these efforts, we strive to keep
as close as we can to 100% code coverage in these tested areas.

In django-fixtureless
---------

.. warning::
    These guides assume that you have already created and activated your
    virtualenv.  If you do not activate your virtualenv, the python
    libraries will be installed globally.

We use Django's test commands to execute tests on django-fixtureless.
This command should be run from **django-fixtureless/fixtureless/tests/test_django_project**.::

    $ django-admin.py test test_app.tests

Notes
-----
We require that tests pass before merging to dev.
