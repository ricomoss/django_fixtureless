from django.db import models


class ModelOne(models.Model):
    decimal_field = models.DecimalField(decimal_places=2, max_digits=10)
    ip_address_field = models.IPAddressField()
    boolean_field = models.BooleanField()
    char_field = models.CharField(max_length=255)
    text_field = models.TextField()
    slug_field = models.SlugField()
    date_field = models.DateField()
    datetime_field = models.DateTimeField()
    integer_field = models.IntegerField()
    positive_integer_field = models.PositiveIntegerField()
    positive_small_integer_field = models.PositiveSmallIntegerField()
    auto_field = models.AutoField(primary_key=True)
    email_field = models.EmailField()
    url_field = models.URLField()
    try:
        from timezone_field import TimeZoneField
        timezone_field = TimeZoneField()
    except ImportError:
        pass


class ModelTwo(models.Model):
    foreign_key = models.ForeignKey(ModelOne, related_name='modeltwo_fk')
    one_to_one = models.OneToOneField(
        ModelOne, related_name='modeltwo_one2one')
    char_field = models.CharField(max_length=20)
