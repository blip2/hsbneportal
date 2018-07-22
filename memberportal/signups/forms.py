from django import forms
from django.forms import ModelForm

from signups.models import Signup, Slot


class SignupForm(forms.Form):
    email = forms.EmailField(label='Email',)


class SignupForm_NoPhone(SignupForm):
    phone = forms.RegexField(
        regex=r'^\+?1?\d{9,15}$',
        error_messages={
            "invalid": "Phone number must be entered in the format: "
            "'+999999999'. Up to 15 digits allowed.", },
        label='Phone',)


class SignupForm_NotMember(SignupForm):
    email = forms.EmailField(label='Email',)
    surname = forms.CharField(label='Surname',)
    forenames = forms.CharField(label='Forenames',)
    phone = forms.RegexField(
        regex=r'^\+?1?\d{9,15}$',
        error_messages={
            "invalid": "Phone number must be entered in the format: "
            "'+999999999'. Up to 15 digits allowed.",
        },
        label='Phone', )


class SignupEditForm(ModelForm):
    name = forms.CharField(label='Signup Name',)
    description = forms.CharField(label='Description', widget=forms.Textarea)
    contact = forms.EmailField(
        label='Contact Email',
        help_text='Contact email address for queries (e.g. show email)')
    audition_notice = forms.CharField(
        label='Audition Notice',
        help_text='Provide a URL link to the audition notice.',
        required=False,)
    # allow_queue = forms.BooleanField(
    #    label='Allow Queue',
    #    help_text='Allow queuing for audition slots if all slots are'
    #              ' full (not recommended unless you are likely to be '
    #              'oversubscribed)',
    #    required=False,)
    visible = forms.BooleanField(
        label='Signup Visible',
        help_text='This makes your signup visible to the public. '
                  'You should enable this after you have added all of your '
                  'slots.',
        required=False,)
    member_only = forms.BooleanField(
        label='Members Only',
        help_text='Only allow members to signup (i.e. members only events)',
        required=False,)
    force_online_payment = forms.BooleanField(
        label='Force Online Payment',
        help_text='An online payment must be paid to confirm a signup'
                  ' slot (recommended)',
        required=False,)
    confirm_info = forms.CharField(
        label='Confirmation Info',
        help_text='Information shown to the user when confiming a place '
                  '(also sent by email)',
        widget=forms.Textarea)

    class Meta:
        model = Signup
        fields = ['name', 'description', 'audition_notice',  # 'allow_queue',
                  'visible', 'member_only', 'force_online_payment',
                  'confirm_info', 'contact', ]


class SignupAddForm(SignupEditForm):
    payment = forms.DecimalField(
        label='Non-Member Cost',
        help_text='Cost for Non-Members (note: this cannot be edited later)',
        min_value=0.0, max_value=100.0)
    member_payment = forms.DecimalField(
        label='Member Cost',
        help_text='Cost for Members (note: this cannot be edited later)',
        min_value=0.0, max_value=100.0)

    class Meta:
        model = Signup
        fields = ['name', 'description', 'audition_notice', 'payment',
                  'member_payment', 'member_only',  # 'allow_queue',
                  'confirm_info', 'force_online_payment', 'contact', ]


class SlotAddForm(ModelForm):
    location = forms.CharField(
        label='Location',
        initial='Brewers Hall Gardens')
    start = forms.DateTimeField(
        label='Start Date/Time',
        input_formats=['%Y-%m-%d %H:%M', ], )
    end = forms.DateTimeField(
        label='End Date/Time',
        input_formats=['%Y-%m-%d %H:%M', ], )
    places = forms.IntegerField(
        label='Number of Places',
        help_text='Number of places in this slot (zero is unlimited)',
        min_value=0.0, max_value=100.0)

    class Meta:
        model = Slot
        fields = ['location', 'start', 'end', 'places']
