from django.db import models
from collectionfield.models import CollectionField
from django.core.validators import RegexValidator
from django.utils.safestring import mark_safe


class User(models.Model):
    name = models.CharField(max_length=200, help_text='Enter user Name')
    middle_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{10,15}$',
        message='Phone number must be entered in the format : 0987654321 or +251987654321 up to 15 digits allowed'
    )
    phone = models.CharField(validators=[phone_regex], max_length=15)
    email = models.EmailField(unique=True)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    department = models.CharField(max_length=200, null=True, blank=True)
    password_regex = RegexValidator(
        regex=r'^\S{6,1024}',
        message='password must be at least 6 character'
    )
    password = models.CharField(validators=[password_regex], max_length=1024)
    sex = models.CharField(max_length=200, choices=(('male', 'male'), ('female', 'female')))
    photo = models.ImageField(upload_to='', blank=True, default='null.png')
    is_active = models.CharField(max_length=200, choices=(('active', True), ('nonactive', False)), default='nonactive')
    register_date = models.DateField()

    def __str__(self):
        return self.name+' '+self.middle_name

    def image_tag(self):
        return mark_safe('<img src="%s" width="150" height="150"/>' % self.photo.url)
    image_tag.short_description = 'Photo'
    image_tag.allow_tags = True


class Organizer(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{10,15}$',
        message='Phone number must be entered in the format : 0987654321 or +251987654321 up to 15 digits allowed'
    )
    phone = models.CharField(validators=[phone_regex], max_length=15)
    email = models.EmailField(unique=True)
    password_regex = RegexValidator(
        regex=r'^\S{6,1024}',
        message='password must be at least 6 character'
    )
    password = models.CharField(validators=[password_regex], max_length=1024)
    photo = models.ImageField(upload_to='', blank=True, default='astu.gif')
    is_active = models.CharField(max_length=200, choices=(('active', True), ('nonactive', False)), default='nonactive')
    register_date = models.DateField()

    def __str__(self):
        return self.name

    def image_tag(self):
        return mark_safe('<img src="%s" width="150" height="150"/>' % self.photo.url)
    image_tag.short_description = 'Photo'
    image_tag.allow_tags = True


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='', blank=True)

    def __str__(self):
        return self.name

    def image_tag(self):
        return mark_safe('<img src="%s" width="150" height="150"/>' % self.photo.url)

    image_tag.short_description = 'Photo'
    image_tag.allow_tags = True


class Interest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    priority = models.PositiveSmallIntegerField(default=10)
    register_date = models.DateField()

    class Meta:
        unique_together = ('user', 'category')

    def __str__(self):
        return self.category.name + ' by ' + self.user.name


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    venue = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    register_date = models.DateField()

    def __str__(self):
        return self.title


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return self.event.title + ' by ' + self.user.name


class Calendar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    venue = models.CharField(max_length=200, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, blank=True, null=True)
    register_date = models.DateField()

    def __str__(self):
        return self.title + ' by ' + self.user.name

    def save(self, *args, **kwargs):
        if self.event is not None:
            conflicting_instance = Calendar.objects.filter(user=self.user, event=self.event)
            if self.id:
                conflicting_instance = conflicting_instance.exclude(pk=self.id)
            if conflicting_instance.exists():
                raise Exception('Calendar with this user and event already exist.')
        super(Calendar, self).save(*args, **kwargs)


class FavouriteOrganization(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        unique_together = ('user', 'organizer')

    def __str__(self):
        return self.organizer.name+' by '+self.user.name
