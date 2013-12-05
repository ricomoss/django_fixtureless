django-fixtureless
====================

Fixtureless Testing Utility for Django.

Requirements:
-----------------

1. Django 1.6
2. Python (2.7+ or 3.3+)
3. PostgreSQL

Todo:
-----------------

1. Support MySQL
2. Support SQLite
3. Create Unit Tests
4. Create a factory for creating groups of model objects


Usage:
-----------------

The purpose behind fixtureless is to provide a fast and easy way to create test objects in Django.  Fixtures are
often used to provide a set of mock data for testing purposes.  It is tedious to update all the fixtures upon a
model update or to create a new set of fixtures if you want to test specific model parameters.  When the
project contains a large amount of fixtures tests also begin to run slowly due to the load time.

Fixtureless is meant to bypass all this.  You can create a fixtureless object given the model and **kwargs
containing any specific data you want to test.

Here is an example using fixtureless.  Suppose you have a model defined as follows.::

    from django.db import models
    from django.contrib.auth.models import AbstractUser

    class User(AbstractUser):
        auth_key = models.CharField(max_length=16)
    
        def __str__(self):
            if self.first_name:
                if self.last_name:
                    return "{0} {1}'s Profile".format(
                        self.first_name, self.last_name)
                else:
                    return "{0}'s Profile".format(self.first_name)
            else:
                return "{0}'s Profile".format(self.username)


This is what a unit test for `__str__` might look like.::

    from django.test import TestCase
    from fixtureless.fixtureless import create_instance
    from my_app.models import User

    class UserTest(TestCase):
        def test_str(self):
            initial = {
                'username': 'test_username',
                'first_name': 'test_first_name',
                'last_name': 'test_last_name',
            }
            user = create_instance(User, **initial)
            user.save()
            expected = "test_first_name test_last_name's Profile"
            self.assertEqual(user.__str__(), expected)
            user.delete()
    
            del(initial['last_name'])
            user = create_instance(User, **initial)
            user.save()
            expected = "test_first_name's Profile"
            self.assertEqual(user.__str__(), expected)
            user.delete()
    
            del(initial['first_name'])
            user = create_instance(User, **initial)
            user.save()
            expected = "test_username's Profile"
            self.assertEqual(user.__str__(), expected)
            user.delete()


Let's look at a more complex relationship.  First the models.::

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
    

We could create a `Charge` object and have access to an automatically generated `Customer` object
due to the `ForeignKey` relationship.::

    from django.test import TestCase
    from fixtureless.fixtureless import create_instance
    from my_app.constants import CURRENCY_USD
    from my_app.models import Charge, Customer

    class ChargeTest(TestCase):
        def test_create_charge_only(self):
            initial = {
                'amount': '50',
                'description': 'test description',
            }
            charge = create_instance(Charge, **initial)
            charge.save()
            
            customer = charge.customer
            self.assertIsNotNone(customer)

        def test_create_charge_with_customer(self):
            initial = {
                'se_id': '1',
                'uuid': 'customer',
                'email': 'test@example.com',
            }
            customer = create_instance(Customer, **initial)
            customer.save()
            
            initial = {
                'amount': '50',
                'customer': customer,
                'description': 'test description',
            }
            charge = create_instance(Charge, **initial)
            charge.save()
            
            self.assertEqual(charge.customer.se_id, customer.se_id)
            

