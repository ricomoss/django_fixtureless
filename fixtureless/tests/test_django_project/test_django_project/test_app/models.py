from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

try:
    from timezone_field import TimeZoneField
except ImportError:
    from django.db.models import DateTimeField as TimeZoneField


class ModelOne(models.Model):
    decimal_field = models.DecimalField(decimal_places=2, max_digits=10)
    ip_address_field = models.GenericIPAddressField()
    boolean_field = models.BooleanField(default=False)
    char_field = models.CharField(max_length=255)
    text_field = models.TextField()
    slug_field = models.SlugField()
    date_field = models.DateField()
    datetime_field = models.DateTimeField()
    integer_field = models.IntegerField()
    small_integer_field = models.SmallIntegerField()
    positive_integer_field = models.PositiveIntegerField()
    positive_small_integer_field = models.PositiveSmallIntegerField()
    auto_field = models.AutoField(primary_key=True)
    email_field = models.EmailField()
    url_field = models.URLField()
    time_field = models.TimeField()
    timezone_field = TimeZoneField(default='America/Denver')
    float_field = models.FloatField()

    image_field = models.ImageField(
        upload_to='./', width_field='image_width',
        height_field='image_height')
    image_width = models.PositiveIntegerField()
    image_height = models.PositiveIntegerField()

    file_field = models.FileField(upload_to='./')
    auto_now_add_field = models.DateTimeField(auto_now_add=True)
    datetime_with_default = models.DateTimeField(default=timezone.now)


class ModelTwo(models.Model):
    foreign_key = models.ForeignKey(
        ModelOne, related_name='modeltwo_fk', on_delete=models.CASCADE)
    one_to_one = models.OneToOneField(
        ModelOne, related_name='modeltwo_one2one', on_delete=models.CASCADE)
    char_field = models.CharField(max_length=20)
    big_auto_field = models.BigAutoField(primary_key=True)


def supply_default():
    return {'method_name': 'supply_default'}


class ModelThree(models.Model):
    json_field = JSONField()
    json_field_list = JSONField(default=list)
    json_field_dict = JSONField(default=dict)
    json_field_callable = JSONField(default=supply_default)
