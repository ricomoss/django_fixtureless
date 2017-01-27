from django.db import models
try:
    from timezone_field import TimeZoneField
except ImportError:
    from django.db.models import DateTimeField as TimeZoneField


class ModelOne(models.Model):
    decimal_field = models.DecimalField(decimal_places=2, max_digits=10)
    ip_address_field = models.IPAddressField()
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
        upload_to='/tmp', width_field='image_width',
        height_field='image_height')
    image_width = models.PositiveIntegerField()
    image_height = models.PositiveIntegerField()

    file_field = models.FileField(upload_to='/tmp')
    auto_now_add_field = models.DateTimeField(auto_now_add=True)


class ModelTwo(models.Model):
    foreign_key = models.ForeignKey(ModelOne, related_name='modeltwo_fk')
    one_to_one = models.OneToOneField(
        ModelOne, related_name='modeltwo_one2one')
    char_field = models.CharField(max_length=20)
