from django import forms
from django.forms import ChoiceField
from .models import User, Organizer, Event, Category, Calendar, Interest
from django.core.validators import RegexValidator
from datetime import datetime
import pytz

import time


class UserRegister(forms.ModelForm):
    password_regex = RegexValidator(
        regex=r'^\S{6,1024}',
        message='password must be at least 6 character'
    )
    user_password = forms.CharField(
        validators=[password_regex],
        max_length=1024,
        widget=forms.PasswordInput(),
        help_text='*Enter your password minimum 6 character',
        label='Password'
    )
    confirm_password = forms.CharField(
        max_length=1024,
        widget=forms.PasswordInput(),
        help_text='*Confirm your password'
    )

    class Meta:
        model = User
        fields = ['name', 'middle_name', 'last_name', 'phone', 'email', 'year', 'department', 'sex', 'user_password',
                  'confirm_password', 'photo']
        help_texts = {
            'name': "* Enter user first name",
            'middle_name': "* Enter user middle name",
            'last_name': "* Enter user last name",
            'phone': "* Enter user phone number",
            'year': "Enter user academic year (if the user is student)",
            'department': "Enter user academic department (if the user is student)",
            'email': "*Enter user email",
            'photo': "Enter user photo (if any)",
            'sex': "* Enter user gender",
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        middle_name = cleaned_data.get('middle_name')
        last_name = cleaned_data.get('last_name')
        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')
        sex = cleaned_data.get('sex')
        user_password = cleaned_data.get('user_password')
        confirm = cleaned_data.get('confirm_password')
        if (not name) or (not middle_name) or (not last_name) or (not phone) or (not email) or (not sex)\
                or (not user_password) or (not confirm):
            raise forms.ValidationError("Please correct the errors below.")

        if user_password and confirm:
            if user_password != confirm:
                raise forms.ValidationError("password is not confirmed")
        try:
            User.objects.get(email=email)
            raise forms.ValidationError("User with this Email already exists.")
        except User.DoesNotExist:
            try:
                Organizer.objects.get(email=email)
                raise forms.ValidationError("Organizer with this Email already exists.")
            except Organizer.DoesNotExist:
                pass
        return cleaned_data


class OrganizerRegister(forms.ModelForm):
    password_regex = RegexValidator(
        regex=r'^\S{6,1024}',
        message='password must be at least 6 character'
    )
    org_password = forms.CharField(
        validators=[password_regex],
        max_length=1024,
        widget=forms.PasswordInput(),
        help_text='*Enter your password minimum 6 character',
        label='Password'
    )
    confirm_password = forms.CharField(
        max_length=1024,
        widget=forms.PasswordInput(),
        help_text='*Confirm your password'
    )

    class Meta:
        model = Organizer
        fields = ['name', 'phone', 'email',  'org_password', 'confirm_password', 'description', 'photo']
        help_texts = {
            'name': "* Enter organization name",
            'description': "Enter the description of the organization",
            'phone': "* Enter organization phone number",
            'email': "*Enter organization email",
            'photo': "Enter organization logo (if any)",
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')
        org_password = cleaned_data.get('org_password')
        confirm = cleaned_data.get('confirm_password')
        if (not name) or (not phone) or (not email) or (not org_password) or (not confirm):
            raise forms.ValidationError("Please correct the errors below.")

        if org_password and confirm:
            if org_password != confirm:
                raise forms.ValidationError("password is not confirmed")
        try:
            Organizer.objects.get(email=email)
            raise forms.ValidationError("Organizer with this Email already exists.")
        except Organizer.DoesNotExist:
            try:
                User.objects.get(email=email)
                raise forms.ValidationError("User with this Email already exists.")
            except User.DoesNotExist:
                pass
        return cleaned_data


class Login(forms.Form):
    email = forms.EmailField(
        max_length=254,
        widget=forms.TextInput(),
    )
    password = forms.CharField(
        max_length=1024,
        widget=forms.PasswordInput(),
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        email = cleaned_data.get('email')

        if (not password) or (not email):
            raise forms.ValidationError("Please correct the errors below.")

        if password and email:
            try:
                user = User.objects.get(email=email)
                _password = user.password
                if user.is_active == 'nonactive':
                    raise forms.ValidationError("Please confirm your email address to complete the registration.")
            except User.DoesNotExist:
                try:
                    organizer = Organizer.objects.get(email=email)
                    _password = organizer.password
                    if organizer.is_active == 'nonactive':
                        raise forms.ValidationError("Please confirm organizer email address to complete "
                                                    "the registration.")
                except Organizer.DoesNotExist:
                    raise forms.ValidationError("Please enter the correct email and password account.Note that "
                                                "both fields may be case-sensitive.")

            if password == _password:
                return
            else:
                raise forms.ValidationError("Please enter the correct email and password account. "
                                            "Note that both fields may be case-sensitive. ")

        return cleaned_data


class EditUserProfile(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user_email = kwargs.pop('user_email')

        super(EditUserProfile, self).__init__(*args, **kwargs)
        self.options = [['male', 'male'], ['female', 'female']]
        user = User.objects.get(email=self.user_email)
        self.email = user.email

        self.initial['sex'] = user.sex
        self.fields['name'] = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            initial=user.name,
        )
        self.fields['middle_name'] = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            initial=user.middle_name,
        )
        self.fields['last_name'] = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            initial=user.last_name,
        )
        phone_regex = RegexValidator(
            regex=r'^\+?1?\d{10,15}$',
            message='Phone number must be entered in the format : 0987654321 or +251987654321 up to 15 digits allowed'
        )
        self.fields['phone'] = forms.CharField(
            validators=[phone_regex],
            max_length=15,
            widget=forms.TextInput(),
            initial=user.phone,
        )

        if user.year != 0 and user.year:
            self.fields['year'] = forms.IntegerField(
                widget=forms.NumberInput,
                min_value=1,
                required=True,
                initial=user.year,
            )
        else:
            self.fields['year'] = forms.IntegerField(
                widget=forms.HiddenInput(),
                required=False,
                initial=user.year,
            )
        if user.department:
            self.fields['department'] = forms.CharField(
                widget=forms.TextInput(),
                max_length=200,
                required=True,
                initial=user.department,
            )
        else:
            self.fields['department'] = forms.CharField(
                widget=forms.HiddenInput(),
                required=False,
                initial=user.department,
            )

        self.fields['email'] = forms.EmailField(
            max_length=254,
            widget=forms.TextInput(),
            initial=user.email,
        )
        self.fields['photo'] = forms.ImageField(
            required=False,
            initial="Images/" + str(user.photo),
        )
        self.fields['sex'] = forms.ChoiceField(
            widget=forms.Select(),
            choices=self.options,
        )

        self.fields['registered_date'] = forms.DateField(
            widget=forms.DateInput(),
            initial=user.register_date,
            disabled=True,
        )

    name = forms.CharField()
    middle_name = forms.CharField()
    last_name = forms.CharField()
    phone = forms.CharField()
    year = forms.IntegerField()
    department = forms.CharField()
    email = forms.EmailField()
    photo = forms.ImageField()
    sex = forms.ChoiceField()
    registered_date = forms.DateField()

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        middle_name = cleaned_data.get('middle_name')
        last_name = cleaned_data.get('last_name')
        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')
        sex = cleaned_data.get('sex')
        if (not name) or (not middle_name) or (not last_name) or (not phone) or (not email) or (not sex):
            raise forms.ValidationError("Please correct the errors below.")

        if email != self.email:
            try:
                Organizer.objects.get(email=email)
                raise forms.ValidationError("Organizer with this Email already exists.")
            except Organizer.DoesNotExist:
                try:
                    User.objects.get(email=email)
                    raise forms.ValidationError("User with this Email already exists.")
                except User.DoesNotExist:
                    pass
        return cleaned_data


class EditOrganizationProfile(forms.Form):

    def __init__(self, *args, **kwargs):
        self.organization_email = kwargs.pop('organization_email')

        super(EditOrganizationProfile, self).__init__(*args, **kwargs)
        organization = Organizer.objects.get(email=self.organization_email)
        self.email = organization.email

        self.fields['name'] = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            initial=organization.name,
        )
        phone_regex = RegexValidator(
            regex=r'^\+?1?\d{10,15}$',
            message='Phone number must be entered in the format : 0987654321 or +251987654321 up to 15 digits allowed'
        )
        self.fields['phone'] = forms.CharField(
            validators=[phone_regex],
            max_length=15,
            widget=forms.TextInput(),
            initial=organization.phone,
        )

        self.fields['email'] = forms.EmailField(
            max_length=254,
            required=False,
            widget=forms.TextInput(),
            initial=organization.email,
        )
        self.fields['photo'] = forms.ImageField(
            required=False,
            initial="Images/" + str(organization.photo),
        )
        self.fields['description'] = forms.CharField(
            max_length=3000,
            required=False,
            widget=forms.Textarea(),
            initial=organization.description,
        )
        self.fields['registered_date'] = forms.DateField(
            widget=forms.DateInput(),
            initial=organization.register_date,
            disabled=True,
        )

    name = forms.CharField()
    phone = forms.CharField()
    email = forms.EmailField()
    description = forms.CharField()
    photo = forms.ImageField()
    registered_date = forms.DateField()

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')
        if (not name) or (not phone) or (not email):
            raise forms.ValidationError("Please correct the errors below.")

        if email != self.email:
            try:
                Organizer.objects.get(email=email)
                raise forms.ValidationError("Organizer with this Email already exists.")
            except Organizer.DoesNotExist:
                try:
                    User.objects.get(email=email)
                    raise forms.ValidationError("User with this Email already exists.")
                except User.DoesNotExist:
                    pass
        return cleaned_data


class ChangePassword(forms.Form):
    def __init__(self, *args, **kwargs):
        self.password = kwargs.pop('key')

        super(ChangePassword, self).__init__(*args, **kwargs)

    old_password = forms.CharField(
        max_length=1024,
        widget=forms.PasswordInput(),
    )
    password_regex = RegexValidator(
        regex=r'^\S{6,1024}',
        message='password must be at least 6 character'
    )
    new_password = forms.CharField(
        validators=[password_regex],
        max_length=1024,
        widget=forms.PasswordInput(),
        help_text='*Enter your new password minimum 6 character'
    )
    confirm = forms.CharField(
        label='Confirm Password',
        max_length=1024,
        widget=forms.PasswordInput(),
        help_text='*Enter your new password again'
    )

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm')
        if (not old_password) or (not new_password) or (not confirm_password):
            raise forms.ValidationError("Please correct the errors below.")

        if old_password == self.password:
            if new_password:
                if new_password == confirm_password:
                    return
                else:
                    raise forms.ValidationError("password is not confirmed")
        else:
            raise forms.ValidationError("Please enter the correct old password. ")

        return cleaned_data


class AddEvent(forms.ModelForm):
    '''
    starting_time = forms.DateTimeField(
        label='Start Time',
        widget=forms.DateTimeInput(),
        help_text="* Enter event date and the starting time",
    )
    ending_time = forms.DateTimeField(
        label='End Time',
        widget=forms.DateTimeInput(),
        required =False,
        help_text="* Enter event date and the starting time",
    )
    '''
    class Meta:
        model = Event
        fields = ['title', 'start_time', 'end_time', 'venue', 'category', 'description']
        help_texts = {
            'title': "* Enter title of the event",
            'start_time': "* Enter event date and the starting time in YYYY-MM-DD HH:MM:SS format"
                          " and 24 hours format",
            'end_time': "Enter event date and the end time in YYYY-MM-DD HH:MM:SS format"
                          " and 24 hours format",
            'venue': "* Enter event venue",
            'category': "Enter category of the event",
            'description': "Enter the description about the event",
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        venue = cleaned_data.get('venue')

        if (not title) or (not start_time) or (not venue):
            raise forms.ValidationError("Please correct the errors below.")
        utc = pytz.UTC
        now = utc.localize(datetime.combine(datetime.now().date(), datetime.max.time()))

        if start_time < now:
            raise forms.ValidationError("Date must be greater than or equal to "+str(datetime.now().date()))
        if end_time:
            if start_time > end_time:
                raise forms.ValidationError("strat time must be less than end time end time.")
        return cleaned_data


class AddCategory(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description','photo']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        if not name:
            raise forms.ValidationError("Please correct the errors below.")

        return cleaned_data


class ForgotPassword(forms.Form):
    email = forms.EmailField(
        max_length=254,
        widget=forms.TextInput(),
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if not email:
            raise forms.ValidationError("Please correct the errors below.")

        if email:
            try:
                User.objects.get(email=email)
            except User.DoesNotExist:
                try:
                    Organizer.objects.get(email=email)
                except Organizer.DoesNotExist:
                    raise forms.ValidationError("Please enter the correct email.")

        return cleaned_data


class EditEvent(forms.Form):

    def __init__(self, *args, **kwargs):
        self.event_id = kwargs.pop('event_id')

        super(EditEvent, self).__init__(*args, **kwargs)
        event = Event.objects.get(pk=self.event_id)
        self.options = [[i.id, i] for i in Category.objects.all().order_by('name')]

        self.initial['category'] = event.category.id
        self.fields['title'] = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            initial=event.title,
            help_text="* Enter title of the event",
        )
        self.fields['start_time'] = forms.DateTimeField(
            widget=forms.DateTimeInput(),
            help_text="* Enter event date and the starting time in YYYY-MM-DD HH:MM:SS format and 24 hours format",
            initial=event.start_time,
        )
        self.fields['end_time'] = forms.DateTimeField(
            widget=forms.DateTimeInput(),
            required=False,
            help_text="Enter event date and the end time in YYYY-MM-DD HH:MM:SS format and 24 hours format",
            initial=event.end_time,
        )
        self.fields['venue'] = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            initial=event.venue,
            help_text="* Enter event venue",
        )
        self.fields['category'] = forms.ChoiceField(
            widget=forms.Select(),
            choices=self.options,
            help_text= "Enter category of the event",
        )
        self.fields['description'] = forms.CharField(
            max_length=3000,
            required=False,
            widget=forms.Textarea(),
            initial=event.description,
            help_text="Enter the description about the event",
        )
        self.fields['registered_date'] = forms.DateField(
            widget=forms.DateInput(),
            initial=event.register_date,
            disabled=True,
        )

    title = forms.CharField()
    start_time = forms.DateTimeField()
    end_time = forms.DateTimeField()
    venue = forms.CharField()
    category = forms.ChoiceField()
    description = forms.CharField()
    registered_date = forms.DateField()

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        start_time = cleaned_data.get('start_time')
        venue = cleaned_data.get('venue')
        category = cleaned_data.get('category')
        if (not title) or (not start_time) or (not venue) or (not category):
            raise forms.ValidationError("Please correct the errors below.")

        return cleaned_data


class EditInterest(forms.Form):

    def __init__(self, *args, **kwargs):
        self.interest_id = kwargs.pop('interest_id')

        super(EditInterest, self).__init__(*args, **kwargs)
        interest = Interest.objects.get(pk=self.interest_id)

        self.fields['name'] = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            initial=interest.category.name,
            disabled=True,
        )
        self.fields['priority'] = forms.IntegerField(
            widget=forms.NumberInput,
            min_value=0,
            max_value=10,
            initial=interest.priority,
            help_text='Enter the priority of the category.It must be between 0 and 10.'
        )
        self.fields['description'] = forms.CharField(
            max_length=3000,
            required=False,
            widget=forms.Textarea(),
            initial=interest.category.description,
            disabled=True,
        )

    name = forms.CharField()
    priority = forms.IntegerField()
    description = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()
        priority = cleaned_data.get('priority')

        if not priority:
            raise forms.ValidationError("Please correct the errors below.")

        return cleaned_data


class AddInterestCategory(forms.Form):

    def __init__(self, *args, **kwargs):
        self.email = kwargs.pop('user_email')

        super(AddInterestCategory, self).__init__(*args, **kwargs)
        user = User.objects.get(email=self.email)
        category = Category.objects.all()
        self.options = [[i.id, i.name] for i in category]
        my_interest = Interest.objects.filter(user=user)
        for i in my_interest:
            self.options.remove([i.category.id, i.category.name])

        self.fields['category'] = forms.ChoiceField(
            widget=forms.Select(),
            choices=self.options,
            help_text="Enter category of the event",
        )
        self.fields['priority'] = forms.IntegerField(
            widget=forms.NumberInput,
            min_value=0,
            max_value=10,
            initial=10,
            help_text='Enter the priority of the category.It must be between 0 and 10.'
        )

    category = forms.ChoiceField()
    priority = forms.IntegerField()

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        priority = cleaned_data.get('priority')

        if not priority or not category:
            raise forms.ValidationError("Please correct the errors below.")

        return cleaned_data


class DateSearchEngine(forms.Form):
    search_date = forms.DateField(
        label='Date',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('search_date')

        if not date:
            raise forms.ValidationError("Please correct the errors below.")

        return cleaned_data


class AddCalendar(forms.Form):
    options = [[i.id, i] for i in Category.objects.all().order_by('name')]
    options.insert(0, [None, '----------'])
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(),
        help_text="* Enter title of the event",
    )
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(),
        help_text="* Enter event date and the starting time in YYYY-MM-DD HH:MM:SS format and 24 hours format",
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(),
        required=False,
        help_text="Enter event date and the end time in YYYY-MM-DD HH:MM:SS format and 24 hours format",
    )
    venue = forms.CharField(
        max_length=200,
        widget=forms.TextInput(),
        required=False,
        help_text="* Enter event venue",
    )
    category = forms.ChoiceField(
        widget=forms.Select(),
        required=False,
        choices=options,
        help_text="Enter category of the event",
    )
    description = forms.CharField(
        max_length=3000,
        required=False,
        widget=forms.Textarea(),
        help_text="Enter the description about the event",
    )

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        start_time = cleaned_data.get('start_time')
        if (not title) or (not start_time):
            raise forms.ValidationError("Please correct the errors below.")

        return cleaned_data
