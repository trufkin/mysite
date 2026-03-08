from django.conf import settings
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title


class Hero(models.Model):
    class Category(models.TextChoices):
        CRAFTSMAN   = 'craftsman',   'Craftsman'
        FARMER      = 'farmer',      'Farmer'
        PLUMBER     = 'plumber',     'Plumber'
        ELECTRICIAN = 'electrician', 'Electrician'
        BUILDER     = 'builder',     'Builder'
        GARDENER    = 'gardener',    'Gardener'
        OTHER       = 'other',       'Other Service'

    name        = models.CharField(max_length=200)
    slug        = models.SlugField(max_length=220, unique=True)
    category    = models.CharField(max_length=30, choices=Category.choices)
    photo       = models.ImageField(upload_to='heroes/photos/', blank=True)
    tagline     = models.CharField(max_length=300, blank=True)
    description_en = models.TextField(blank=True, verbose_name='Description (EN)')
    description_ro = models.TextField(blank=True, verbose_name='Description (RO)')
    description_ru = models.TextField(blank=True, verbose_name='Description (RU)')
    services    = models.TextField(blank=True, help_text='Services offered — comma-separated or free text')
    phone       = models.CharField(max_length=30, blank=True)
    email       = models.EmailField(blank=True)
    is_active   = models.BooleanField(default=True)
    order       = models.PositiveSmallIntegerField(default=0, help_text='Lower number = displayed first')
    created     = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Hero'
        verbose_name_plural = 'Heroes'

    def __str__(self):
        return self.name

    def get_description(self, lang='en'):
        """Return description in requested language, falling back to EN."""
        desc = getattr(self, f'description_{lang}', '')
        return desc or self.description_en


class Listing(models.Model):
    owner       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings',
    )
    title       = models.CharField(max_length=200)
    description = models.TextField()
    price       = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text='Leave blank if not applicable',
    )
    is_active   = models.BooleanField(default=True)
    created     = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    """Extends the built-in User with email confirmation status."""
    user            = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} profile'
