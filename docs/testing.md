# Testing

Testing is an important part of the maintainability of django-fixtureless. We focus on building automated testing for the functions/methods and classes of django-fixtureless. With these efforts, we strive to keep as close as we can to 100% code coverage in these tested areas.

## In django-fixtureless

**Note:** These guides assume that you have already created and activated your virtualenv.  If you do not activate your virtualenv, the python libraries will be installed globally.

This project uses `tox` for all testing.  This ensures a consistent environment set for testing.

1.  Run the `tox` command from your terminal.

        $ cd /path/to/django_fixtureless; tox
         

Notes
-----
We require that tests pass before merging to master.
