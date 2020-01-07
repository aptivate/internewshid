from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    PasswordResetForm, UserChangeForm, UserCreationForm
)
from django.contrib.auth.tokens import default_token_generator
from django.forms import HiddenInput, ImageField, ModelForm, ValidationError
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext as _

import floppyforms as forms
from form_utils.forms import BetterModelForm

import mail

from .models import User

TITLES = (
    _("Dr"), _("Hon"), _("Mrs"), _("Ms"), _("Mr"), _("Prof"),
    _("His Excellency"), _("Her Excellency"), _("Rt.Hon"), _("Assoc. Prof")
)


class TitleInput(forms.TextInput):
    def get_context_data(self):
        ctx = super(TitleInput, self).get_context_data()
        ctx.update({
            'datalist': TITLES
        })
        return ctx


#######################################################################
# Contacts forms
#######################################################################
class UpdatePersonalInfoForm(BetterModelForm):
    picture = ImageField(required=False)

    class Meta:
        model = User
        fieldsets = [('all', {'fields': [
            'business_email', 'title', 'first_name',
            'last_name', 'personal_email',
            # Address
            'home_address', 'business_address', 'country', 'nationality',
            # Personal info
            'gender', 'contact_type',
            # Work
            'job_title', 'area_of_specialisation',
            # Phones & fax
            'home_tel', 'business_tel', 'mobile', 'fax',
            # IM
            'skype_id', 'yahoo_messenger', 'msn_id',
            'notes', 'picture']})]

        widgets = {
            'title': TitleInput,
        }


class AddContactForm(BetterModelForm):
    picture = ImageField(required=False)

    class Meta:
        model = User
        fieldsets = [('all', {'fields': [
            'business_email', 'title', 'first_name',
            'last_name', 'personal_email', 'is_active',
            # Address
            'home_address', 'business_address', 'country', 'nationality',
            # Personal info
            'gender',
            # Work
            'job_title', 'area_of_specialisation',
            # Phones & fax
            'home_tel', 'business_tel', 'mobile', 'fax',
            # IM
            'skype_id', 'yahoo_messenger', 'msn_id',
            'notes', 'picture']})]
        widgets = {
            'title': TitleInput,
        }


class UpdateContactForm(AddContactForm):
    def notify_email_change(self,
                            old_address,
                            new_address,
                            subject=_('{0}: email change notification').format(settings.SITE_NAME),
                            template_name='contacts/email/email_changed_body.email'):
        ctx = {
            'user': self.instance,
            'old_email': old_address,
            'new_email': new_address
        }
        options = {
            'subject': subject,
            'to': [old_address, new_address],
            'template_name': template_name,
            'context': ctx
        }
        mail.notify(options)

    def save(self, *args, **kwargs):
        if self.instance and self.instance.has_usable_password():
            old = self._meta.model.objects.get(pk=self.instance.pk)
            old_email = old.business_email
            if self.cleaned_data['business_email'] != old_email:
                self.notify_email_change(
                    old_email,
                    self.cleaned_data['business_email'])
        return super(UpdateContactForm, self).save(*args, **kwargs)


class DeleteContactForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(DeleteContactForm, self).__init__(*args, **kwargs)
        self.fields['id'].widget = HiddenInput()

    class Meta:
        model = User
        fields = ('id',)


#######################################################################
# Admin contacts forms
#######################################################################
class AdminUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """

    def __init__(self, *args, **kargs):
        super(AdminUserCreationForm, self).__init__(*args, **kargs)

    class Meta:
        model = User
        fields = ("business_email",)


class AdminUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    def __init__(self, *args, **kargs):
        super(UserChangeForm, self).__init__(*args, **kargs)

    class Meta:
        model = User
        fields = '__all__'


#######################################################################
# Password reset forms
#######################################################################
class ContactPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        """
        Validates that an active user exists with the given email address.
        """
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        self.users_cache = UserModel._default_manager.filter(
            business_email__iexact=email)
        if not len(self.users_cache):
            raise ValidationError(
                _("User with email '{}' not known").format(email)
            )
        if not any(user.is_active for user in self.users_cache):
            # none of the filtered users are active
            raise ValidationError(
                _("User with email '{}' not known".format(email))
            )
        return email

    def save(self, subject,
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        for user in self.users_cache:
            ctx = {
                'email': user.business_email,
                'site': settings.SITE_HOSTNAME,
                'uid': urlsafe_base64_encode(str(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            options = {
                'subject': subject,
                'from_email': from_email,
                'to': [user.business_email],
                'template_name': email_template_name,
                'context': ctx
            }

            mail.notify(options)
