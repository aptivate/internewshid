import os.path

from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db.models import (
    BooleanField, CharField, DateTimeField, EmailField, ImageField, TextField
)
from django.utils import timezone
from django.utils.translation import ugettext as _

from .countries import COUNTRIES, NATIONALITIES

GENDER_CHOICES = (('female', _('Female')),
                  ('male', _('Male')),
                  ('other', _('Other')))


def get_user_fields(instance):
    return (instance.business_email, instance.last_name, instance.first_name)


def get_picture_path(instance, filename):
    name = "_".join([instance.last_name, instance.first_name]).strip('_')
    prefix = name if name else instance.business_email
    new_filename = "{0}_{1}".format(prefix, filename)
    new_path = os.path.join('pictures', new_filename)

    return new_path


# Managers
class UserManager(BaseUserManager):

    def _create_user(self, business_email=None, password=None,
                     is_active=True, is_staff=False, is_superuser=False,
                     **extra_fields):
        now = timezone.now()
        if not business_email:
            raise ValueError(_('The given business_email must be set'))
        email = UserManager.normalize_email(business_email)
        user = self.model(business_email=email, is_staff=is_staff,
                          is_active=is_active, is_superuser=is_superuser,
                          last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, business_email=None, password=None, **extra_fields):
        return self._create_user(business_email, password, **extra_fields)

    def create_superuser(self, business_email, password, **extra_fields):
        return self._create_user(business_email, password, is_staff=True,
                                 is_superuser=True, **extra_fields)


# Models
class User(AbstractBaseUser, PermissionsMixin):
    # Account info
    business_email = EmailField(max_length=190, unique=True, verbose_name='Email')
    is_staff = BooleanField(
        verbose_name='staff status',
        default=False,
        help_text=_("Designates whether the user can log into this admin "
                    "site."))
    is_active = BooleanField(
        verbose_name='active',
        default=True,
        help_text=_("Designates whether this user should be treated as "
                    "active. Unselect this instead of deleting accounts."))
    date_joined = DateTimeField(default=timezone.now)

    # general contact information
    title = CharField(max_length=32)
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    gender = CharField(max_length=6, choices=GENDER_CHOICES)
    contact_type = CharField(max_length=32,
                             verbose_name=_("Type of Contact"))
    # Address
    home_address = TextField(blank=True)
    business_address = TextField(blank=True)
    country = CharField(max_length=64,
                        blank=True,
                        choices=COUNTRIES,
                        help_text=_("The country in which the contact is "
                                    "currently working in"))
    nationality = CharField(max_length=64, blank=True, choices=NATIONALITIES)

    # Work
    job_title = CharField(max_length=64, blank=True)
    area_of_specialisation = CharField(max_length=128, blank=True)

    # Email
    personal_email = EmailField(blank=True)

    # IM
    skype_id = CharField(max_length=32, blank=True)
    yahoo_messenger = CharField(max_length=32,
                                blank=True,
                                verbose_name=_("Yahoo Messenger"))
    msn_id = CharField(max_length=32, blank=True, verbose_name=_("MSN ID"))

    # Phones & fax
    home_tel = CharField(max_length=20,
                         blank=True,
                         verbose_name=_("Home telephone"))
    business_tel = CharField(max_length=20,
                             blank=True,
                             verbose_name=_("Business telephone"))
    mobile = CharField(max_length=20, blank=True)
    fax = CharField(max_length=20, blank=True, verbose_name=_("Fax no"))

    # Misc
    notes = TextField(blank=True)
    picture = ImageField(null=True,
                         blank=True,
                         upload_to=get_picture_path)

    # Managers and book-keeping

    USERNAME_FIELD = 'business_email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def get_full_name(self):
        return u"{1}, {0}".format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def __unicode__(self):
        return self.get_full_name()

    @property
    def email(self):
        return self.business_email

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
