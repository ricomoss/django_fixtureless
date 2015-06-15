django-fixtureless
====================

Fixtureless Testing Utility for Django.  (ver. 1.4.3.1)

The purpose behind fixtureless is to provide a fast and easy way to create
test objects in Django.  Fixtures are often used to provide a set of mock data
for testing purposes.  It is tedious to update all the fixtures upon a model
update or to create a new set of fixtures if you want to test specific model
parameters.  When the project contains a large amount of fixtures tests also
begin to run slowly due to the load time.

Fixtureless is meant to bypass all this.  You can create a fixtureless object
given the model, the number of objects you want created and an `initial`
dictionary containing any specific data you want to test.


Requirements
-----------------

1. Django 1.4 - 1.8
2. Python (2.7+ or 3.3+)

Supports
-----------------

1. PostgreSQL
2. SQLite
3. MySQL (Only Python 2.7+)
4. django-timezone-field (As of ver. 1.2.0)

Install
-----------------

django-fixtureless is registered with Pypi and can be installed using `pip`.

    pip install django-fixtureless


Releases and Branches
-----------------

The master branch is meant for release.  Upon an update to the master branch
the version will increment according to the format: (major).(minor).(micro)

The dev branch holds all approved updates to the django-fixtureless project
until a release milestone is met, at which time dev will be merged into master.

Development is done on branches from dev and merge via pull requests into dev.
Everyone is encouraged to fork this repo and create pull requests with
additions they would like to see in the project.


API Definition
-----------------

Fixtureless has two methods for use in the API.

1.  The `build()` method will generate a Django model object and return the
    object (or list of objects).
2.  The `create()` method is similar to `build()` but the object gets saved to
    the database.

Both methods expect the same arguments.

    from fixtureless import Factory

    from my_app.models import MyModel

    factory = Factory()
    factory.build(MyModel[, count] | [, initial])


Usage
-----------------
There are several available options to use with the fixtureless factory.  Below
are examples of each.

First let's define a few Django models to use in the examples.:

    from django.db import models
    from my_app import constants

    class Customer(models.Model):
        uuid = models.CharField(max_length=50, db_index=True, unique=True)
        account_balance = models.IntegerField(max_length=12, default=0)
        email = models.EmailField()
        se_id = models.IntegerField(db_index=True, unique=True)

        def __str__(self):
            return 'se_id: {}'.format(self.se_id)

    class Charge(TimestampMixin, BaseModel):
        amount = models.PositiveIntegerField(max_length=12, default=50)
        capture = models.BooleanField(default=True)
        currency = models.CharField(
            max_length=5, choices=constants.CURRENCY_CHOICES,
            default=constants.CURRENCY_USD)
        customer = models.ForeignKey(Customer, to_field='uuid')
        description = models.CharField(max_length=255)

        def __str__(self):
            return 'created_at: {}, amount: ${:0.2f}'.format(
                self.created_at, self.amount/100)

Example 1: Trivial Case - A single object:

    from fixtureless import Factory

    from my_app.models import Charge

    factory = Factory()
    charge = factory.create(Charge)


Example 2: Model w/ single count:

    from fixtureless import Factory

    from my_app.models import Charge

    factory = Factory()
    count = 1
    charge = factory.create(Charge, count)


Note:

    Example 1 and Example 2 will both yield a single generated charge object
    with random data.

Example 3: Model w/ multiple count::

    from fixtureless import Factory

    from my_app.models import Charge

    factory = Factory()
    count = 5
    charges = factory.create(Charge, count)


Note:

    Example 3 will return a list with 5 *charge* objects.  All will be unique and
    contain random data.

Example 4: Model w/ single count and initial::

    from fixtureless import Factory

    from my_app.models import Charge

    factory = Factory()
    initial = {
        'amount': '50',
        'description': 'test description',
    }
    charge = factory.create(Charge, initial)


Note:

    Example 4 will create a single charge object with the *amount* and
    *description* fields containing the data provided in the *initial*
    dictionary.  It should be emphasized that you must provide either *count*
    or *initial* data.

Example 5: Model w/ multi count and single initial::

    from fixtureless import Factory

    from my_app.models import Charge

    factory = Factory()
    count = 2
    initial = {
        'amount': '50',
        'description': 'test description',
    }
    initial_list = list()
    for _ in itertools.repeat(None, count):
        initial_list.append(initial)
    charges = factory.create(Charge, initial_list)

Note:

    Example 5 will create two unique charge objects passed back in the
    *charges* list.  Both objects will contain the same *initial* data.  All
    other fields will be randomly generated.

Example 6: Model /w multi count and multi intial::

    from fixtureless import Factory

    from my_app.models import Charge

    factory = Factory()
    initial1 = {
        'amount': '50',
        'description': 'test description 1',
    }
    initial2 = {
        'amount': '150',
        'description': 'test description 2',
    }
    initial_list = [initial1, initial2]
    charges = factory.create(Charge, initial_list)

Note:

    Example 6 will create two unique *Charge* objects passed back in the
    *charges* list.  The first item will contain *initial1* data and the second
    will contain *initial2* data.

Example 7: Multi Model Trivial::

    from fixtureless import Factory

    from my_app.models import Charge, Customer

    factory = Factory()
    objs = factory.create((Charge, ), (Customer, ))

Note:

    Example 7 will create a *Charge* object and a *Customer* object passed back
    in the *objs* list.  It should be empahsized that each object should be
    passed in as it's own *tuple* object.

Example 8: Multi Model w/ counts::

    from fixtureless import Factory

    from my_app.models import Charge, Customer

    factory = Factory()
    count1 = 1
    count2 = 2
    args = ((Charge, count1), (Customer, count2))
    objs = factory.create(*args)

Note:

    Example 8 will create a *Charge* object followed by two *Customer* objects
    passed back in the *objs* list.

Example 9: Multi Model w/ counts and initial::

    from fixtureless import Factory

    from my_app.models import Charge

    factory = Factory()
    count1 = 2
    count2 = 3
    initial1 = {
        'amount': '50',
        'description': 'test description 1',
    }
    initial_list1 = list()
    for _ in itertools.repeat(None, count1):
        initial_list.append(initial1)
    initial2 = {
        'account_balance': '10',
        'email': 'test@example.com',
    }
    initial_list2 = list()
    for _ in itertools.repeat(None, count2):
        initial_list2.append(initial)
    args = ((Charge, initial_list1), (Customer, initial_list2))
    objs = factory.create(*args)

Note:

    Example 9 will create two *Charge* objects with *initial1* data followed by
    three *Customer* objects with *initial2* data passed back in the *objs*
    list.

Example 10: Multi Model w/ counts and multi initial::

    from fixtureless import Factory

    from my_app.models import Charge

    factory = Factory()
    count1 = 2
    count2 = 3
    initial1_1 = {
        'amount': '50',
        'description': 'test description 1',
    }
    initial1_2 = {
        'amount': '150',
        'description': 'test description 2',
    }
    initial2_1 = {
        'account_balance': '10',
        'email': 'test@example.com',
    }
    initial2_2 = {
        'account_balance': '150',
        'email': 'test2@example.com',
    }
    initial2_3 = {
        'account_balance': '250',
        'email': 'test3@example.com',
    }
    initial1_list = [initial1_1, initial1_2]
    initial2_list = [initial2_1, initial2_2, initial2_3]
    args = ((Charge, initial1_list), (Customer, initial2_list))
    objs = factory.create(*args)

Note:

    Example 10 will create two *Charge* objects, one for each *initia1_x*,
    followed by three *Customer* objects, one for each *initial2_x*.
