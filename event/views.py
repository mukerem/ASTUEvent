from django.shortcuts import render_to_response, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404, JsonResponse, FileResponse
from django.contrib import messages
from django.db import IntegrityError
from .models import User, Organizer, Calendar, Interest, Event, Category, FavouriteOrganization, Notification
from .forms import UserRegister, OrganizerRegister, Login, EditUserProfile, ChangePassword, EditOrganizationProfile,\
    AddEvent, AddCategory, ForgotPassword, EditEvent, EditInterest, AddInterestCategory, DateSearchEngine, AddCalendar
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.contrib import messages
from datetime import datetime
import pytz
# Create your views here.


def homepage(request):
    return render_to_response('webpages/homepage.html')


def user_register(request):

    if request.method == "POST":
        form = UserRegister(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            date = datetime.now().date()
            password = request.POST.get('user_password')
            if request.FILES.get('photo'):
                post.photo = request.FILES.get('photo')
            post.register_date = date
            post.password = password
            # post.is_active = 'nonactive'
            post.is_active = 'active'
            # email_confirmation(request, post.email, post)
            post.save()
            messages.success(request, "signup successfully.")

            # messages.success(request, "Please confirm your email address to complete the registration.")
    else:
        form = UserRegister()
    return render(request, 'webpages/user_register.html', {'form': form})


def organization_register(request):

    if request.method == "POST":
        form = OrganizerRegister(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            date = datetime.now().date()
            password = request.POST.get('org_password')
            if request.FILES.get('photo'):
                post.photo = request.FILES.get('photo')
            post.register_date = date
            post.password = password
            # post.is_active = 'nonactive'
            post.is_active = 'active'
            # email_confirmation(request, post.email, post)
            post.save()
            messages.success(request, "signup successfully.")
            # messages.success(request, "Please confirm your email address to complete the registration.")
    else:
        form = OrganizerRegister()
    return render(request, 'webpages/organization_register.html', {'form': form})


def login(request):
    if request.method == "POST":
        form = Login(request.POST)
        if form.is_valid():
            email = request.POST.get('email')

            try:
                User.objects.get(email=email)
                request.session['user_auth'] = email
                return redirect('/notification/')
            except User.DoesNotExist:
                try:
                    Organizer.objects.get(email=email)
                    request.session['organization_auth'] = email
                    return redirect('/organization-event/')
                except Organizer.DoesNotExist:
                    raise Http404("e-mail does not exist")

    else:
        form = Login()
    return render(request, 'webpages/login.html', {'form': form})


def logout(request, role):
    if role == 'user':
        request.session['user_auth'] = None
    elif role == 'organization':
        request.session['organizer_auth'] = None
    else:
        pass
    return redirect('/homepage/')


def notification(request):
    email = request.session.get('user_auth')
    if email:
        user = User.objects.get(email=email)
        if request.method == "POST":
            form = DateSearchEngine(request.POST)
            if form.is_valid():
                date = request.POST.get('search_date')
                notify = Notification.objects.filter(user=user, event__start_time__date=date)
                event = [i.event for i in notify]
                event = sorted(event, key=lambda x: x.register_date, reverse=True)

                my_calendar = Calendar.objects.filter(user=user).exclude(event=None)
                calendar = {}
                for i in my_calendar:
                    calendar[i.event.id] = True

                for i in event:
                    if not calendar.get(i.id):
                        calendar[i.id] = False

                return render(request, 'webpages/notification.html',
                              {'event': event, 'form': form, 'calendar': calendar, 'date': date})

            return render(request, 'webpages/notification.html', {'form': form, 'date': None})
        else:
            form = DateSearchEngine()
            notify = Notification.objects.filter(user=user)
            event = [i.event for i in notify]
            event = sorted(event, key=lambda x: x.register_date, reverse=True)

            my_calendar = Calendar.objects.filter(user=user).exclude(event=None)
            calendar = {}
            for i in my_calendar:
                calendar[i.event.id] = True

            for i in event:
                if not calendar.get(i.id):
                    calendar[i.id] = False

            return render(request, 'webpages/notification.html',
                          {'event': event, 'form': form, 'calendar': calendar, 'date': None})

    else:
        raise Http404("You are not logged in.")


def add_to_calendar(request, event_id, types):
    email = request.session.get('user_auth')
    if email:
        user = User.objects.get(email=email)
        event = Event.objects.get(id=event_id)
        date = datetime.now().date()
        try:
            insert = Calendar(user=user, title=event.title, description=event.description, start_time=event.start_time,
                              end_time=event.end_time, venue=event.venue, organizer=event.organizer,
                              category=event.category, register_date=date, event=event)
            insert.save()
            messages.success(request, "The event "+event.title+" was added to calendar successfully.")
        except Exception:
            calendar = Calendar.objects.get(user=user, event=event)
            calendar.delete()
            messages.success(request, "This event "+event.title+" was removed from calendar successfully.")

        '''
        if types == 'notify':
            return redirect('/notification/')
        elif types == 'favourite':
            return redirect('/favourite-category-events/')
        elif types == 'calendar':
            return redirect('/view-calendar/')
        elif types == 'organization':
            return redirect('/view-event/')
        else:
            return redirect('/view-event/')
        '''
        url = request.META['HTTP_REFERER']
        return redirect(url)
    else:
        raise Http404("You are not logged in.")


def view_user_profile(request):
    user_email = request.session.get('user_auth')
    if not user_email:
        raise Http404("You are not Logged in")
    if request.method == "POST":
        form = EditUserProfile(request.POST, request.FILES, user_email=user_email)
        if form.is_valid():
            user = User.objects.get(email=user_email)
            user.name = request.POST.get('name')
            user.middle_name = request.POST.get('middle_name')
            user.last_name = request.POST.get('last_name')
            user.phone = request.POST.get('phone')
            user.email = request.POST.get('email')
            user.year = request.POST.get('year')
            user.department = request.POST.get('department')
            user.sex = request.POST.get('sex')
            if request.FILES.get('photo'):
                user.photo = request.FILES.get('photo')
            user.save()
            if request.session['user_auth'] != request.POST.get('email'):
                user.is_active = False
                user.save()
                email_confirmation(request, request.POST.get('email'), user)
                request.session['user_auth'] = request.POST.get('email')

            messages.success(request, "The user "+user.name+" was update successfully.")
            return redirect('/user-profile/')

    else:
        form = EditUserProfile(user_email=user_email)
    return render(request, 'webpages/user_profile.html', {'form': form})


def change_password(request, role):
    if role == 'user':
        user_email = request.session.get('user_auth')
        if user_email:
            user = User.objects.get(email=user_email)
            if request.method == "POST":
                form = ChangePassword(request.POST, key=user.password)
                if form.is_valid():
                    user.password = request.POST.get('new_password')
                    user.save()
                    messages.success(request, "The password was changed successfully.")
                    return HttpResponseRedirect('/user-profile/')

            else:
                form = ChangePassword(key=user.password)
        else:
            raise Http404("You are not logged in")

    elif role == 'organization':
        organization_email = request.session.get('organization_auth')
        if organization_email:
            organization = Organizer.objects.get(email=organization_email)
            if request.method == "POST":
                form = ChangePassword(request.POST, key=organization.password)
                if form.is_valid():
                    organization.password = request.POST.get('new_password')
                    organization.save()
                    messages.success(request, "The password was changed successfully.")
                    return HttpResponseRedirect('/organization-profile/')
            else:
                form = ChangePassword(key=organization.password)
        else:
            raise Http404("You are not logged in")

    else:
        raise Http404("You are not logged in")

    return render(request, 'webpages/change_password.html', {'form': form})


def view_organization_event(request):
    email = request.session.get('organization_auth')
    if email:
        organizer = Organizer.objects.get(email=email)

        if request.method == "POST":
            form = DateSearchEngine(request.POST)
            if form.is_valid():
                date = request.POST.get('search_date')
                event = Event.objects.filter(organizer=organizer, start_time__date=date)
                event = sorted(event, key=lambda x: x.register_date, reverse=True)
                return render(request, 'webpages/view_event_by_organization.html',
                              {'event': event, 'form': form, 'date': date})

            return render(request, 'webpages/view_event_by_organization.html', {'form': form, 'date': None})
        else:
            form = DateSearchEngine()
            event = Event.objects.filter(organizer=organizer)
            event = sorted(event, key=lambda x: x.register_date, reverse=True)
            return render(request, 'webpages/view_event_by_organization.html',
                          {'event': event, 'form': form, 'date': None})

    else:
        raise Http404("You are not logged in.")


def view_organization_profile(request):
    organization_email = request.session.get('organization_auth')
    if not organization_email:
        raise Http404("You are not Logged in")
    if request.method == "POST":
        form = EditOrganizationProfile(request.POST, request.FILES, organization_email=organization_email)
        if form.is_valid():
            organization = Organizer.objects.get(email=organization_email)
            organization.name = request.POST.get('name')
            organization.description = request.POST.get('description')
            organization.phone = request.POST.get('phone')
            organization.email = request.POST.get('email')
            if request.FILES.get('photo'):
                organization.photo = request.FILES.get('photo')
                organization.save()
            if request.session['organization_auth'] != request.POST.get('email'):
                organization.is_active = False
                organization.save()
                email_confirmation(request, request.POST.get('email'), organization)
                request.session['organization_auth'] = request.POST.get('email')
            messages.success(request, "The organization "+organization.name+" was update successfully.")
            return redirect('/organization-profile/')

    else:
        form = EditOrganizationProfile(organization_email=organization_email)
    return render(request, 'webpages/organization_profile.html', {'form': form})


def add_event(request):
    organization_email = request.session.get('organization_auth')
    if not organization_email:
        raise Http404("You are not Logged in")
    if request.method == "POST":
        form = AddEvent(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            organization = Organizer.objects.get(email=organization_email)
            date = datetime.now().date()
            post.register_date = date
            post.organizer = organization
            post.save()
            messages.success(request, "The event " + post.title + " was added successfully.")

            message = 'title: '+post.title+"\n"
            message += 'starting time and date: '+str(post.start_time)+'\n'
            if post.end_time:
                message += 'ending time and date: ' + str(post.end_time) + '\n'
            message += 'venue: ' + post.venue + '\n'
            message += 'organizer: ' + str(post.organizer.name) + '\n'
            if post.description:
                message += 'description: ' + str(post.description) + '\n'

            subject = 'This mail is from ASTUEvent Organizer.'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = []

            favourite_user = FavouriteOrganization.objects.filter(organizer=organization)
            total_calendar = Calendar.objects.all()
            calendar = {}
            for i in favourite_user:
                calendar[i.user] = []

            for i in total_calendar:
                user = i.user
                if user in calendar:
                    calendar[user].append(i)
            # print(calendar)
            for each in calendar:
                busy = False
                # replace = False
                new_event_priority = 0
                try:
                    x = Interest.objects.get(user=each, category=post.category)
                    new_event_priority = x.priority
                except Interest.DoesNotExist:
                    pass
                for i in calendar[each]:
                    # print(i.start_time, i.end_time, post.start_time, post.end_time)
                    utc = pytz.UTC
                    if not post.end_time:
                        post.end_time = utc.localize(datetime.combine(post.start_time.date(), datetime.max.time()))

                    if not i.end_time:
                        i.end_time = utc.localize(datetime.combine(i.start_time.date(), datetime.max.time()))

                    if post.start_time >= i.start_time:
                        if post.start_time <= i.end_time:
                            replaced_event_priority = 0
                            try:
                                x = Interest.objects.get(user=each, category=i.category)
                                replaced_event_priority = x.priority
                            except Interest.DoesNotExist:
                                pass
                            print(new_event_priority, replaced_event_priority)
                            if new_event_priority < replaced_event_priority:
                                busy = True
                            '''
                            else:
                                replace = True
                                obj = i.event
                            break
                            '''
                    elif post.end_time >= i.start_time:
                        if post.end_time <= i.end_time:
                            replaced_event_priority = 0
                            try:
                                x = Interest.objects.get(user=each, category=i.category)
                                replaced_event_priority = x.priority
                            except Interest.DoesNotExist:
                                pass
                            print(new_event_priority, replaced_event_priority)
                            if new_event_priority < replaced_event_priority:
                                busy = True
                            '''
                            else:
                                replace = True
                                obj = i.event
                            '''
                            break
                    else:
                        continue
                if not busy:
                    recipient_list.append(each.email)
                    insert = Notification(user=each, event=post)
                    insert.save()
                    ''' if replace:
                        try:
                            notify = Notification.objects.get(user=each, event=obj)
                            notify.delete()
                        except Notification.DoesNotExist:
                            pass '''

                else:
                    continue
            send_mail(subject, message, email_from, recipient_list, fail_silently=False)
            return redirect('/add-event/')

    else:
        form = AddEvent()
    return render(request, 'webpages/add_event.html', {'form': form})


def add_category(request):
    organization_email = request.session.get('organization_auth')
    if not organization_email:
        raise Http404("You are not Logged in")
    if request.method == "POST":
        form = AddCategory(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            messages.success(request, "The category " + post.name + " was added successfully.")
            return redirect('/add-category/')

    else:
        form = AddCategory()
    return render(request, 'webpages/add_category.html', {'form': form})


def view_category(request):
    organization_email = request.session.get('organization_auth')
    if not organization_email:
        raise Http404("You are not Logged in")
    category = Category.objects.all().order_by('name')
    for i in category:
        i.image = "Images/" + str(i.photo)
    return render(request, 'webpages/view_category.html', {'category': category})


def forgot_password(request):
    if request.method == "POST":
        form = ForgotPassword(request.POST)
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        secret_key = get_random_string(8, chars)

        if form.is_valid():
            email = request.POST.get('email')
            recipient_list = [email]
            message = secret_key
            subject = 'This mail is from ASTUEvent Organizer.'
            email_from = settings.EMAIL_HOST_USER

            try:
                user = User.objects.get(email=email)

                send_mail(subject, message, email_from, recipient_list, fail_silently=False)
                user.password = secret_key
                user.save()
            except User.DoesNotExist:
                try:
                    organization = Organizer.objects.get(email=email)
                    send_mail(subject, message, email_from, recipient_list, fail_silently=False)
                    organization.password = secret_key
                    organization.save()
                except Organizer.DoesNotExist:
                    raise Http404("Your E-mail is invalid please insert valid E-mail")
            return redirect('/login/')

    else:
        form = ForgotPassword()
    return render(request, 'webpages/forget_password.html', {'form': form})


def view_event(request):

    email = request.session.get('user_auth')
    if email:
        user = User.objects.get(email=email)
        if request.method == "POST":
            form = DateSearchEngine(request.POST)
            if form.is_valid():
                date = request.POST.get('search_date')
                event = Event.objects.filter(start_time__date=date)

                my_calendar = Calendar.objects.filter(user=user).exclude(event=None)
                calendar = {}
                for i in my_calendar:
                    calendar[i.event.id] = True

                for i in event:
                    if not calendar.get(i.id):
                        calendar[i.id] = False

                return render(request, 'webpages/view_event_by_user.html',
                              {'event': event, 'form': form, 'calendar': calendar, 'date': date})

            # return render(request, 'webpages/view_book_borrow_by_admin.html', {'form': form, 'date': None})

            return render(request, 'webpages/view_event_by_user.html',
                          {'form': form, 'date': None})
        else:
            form = DateSearchEngine()
            event = Event.objects.all().order_by('register_date').reverse()

            my_calendar = Calendar.objects.filter(user=user).exclude(event=None)
            calendar = {}
            for i in my_calendar:
                calendar[i.event.id] = True

            for i in event:
                if not calendar.get(i.id):
                    calendar[i.id] = False
            print(calendar)
            return render(request, 'webpages/view_event_by_user.html',
                          {'event': event, 'form': form, 'calendar': calendar, 'date': None})
        # return render(request, 'webpages/view_event_by_user.html', {'event': event})
    else:
        raise Http404("You are not logged in.")


def view_organization(request):
    email = request.session.get('user_auth')
    if email:
        user = User.objects.get(email=email)
        all_organizer = Organizer.objects.all().order_by('name')
        favourite_organizer_list = FavouriteOrganization.objects.filter(user=user)
        favourite_organizer = [i.organizer for i in favourite_organizer_list]
        organizer = [i for i in all_organizer]
        for i in favourite_organizer:
            organizer.remove(i)

        for i in organizer:
            i.image = "Images/" + str(i.photo)

        return render(request, 'webpages/organization_list.html', {'organizer': organizer})
    else:
        raise Http404("You are not logged in.")


def add_favourite_organization(request, organization_id):
    email = request.session.get('user_auth')
    if email:
        try:
            organization = Organizer.objects.get(pk=organization_id)
            user = User.objects.get(email=email)

            date = datetime.now().date()
            insert = FavouriteOrganization(date=date, user=user, organizer=organization)
            insert.save()
            messages.success(request, "The organization " + organization.name + " was added to favourite successfully.")
            return HttpResponseRedirect('/view-organization/')
        except Organizer.DoesNotExist or User.DoesNotExist:
            raise Http404("You are not logged in or organization is not registered.")

    else:
        raise Http404("You are not logged in")


def view_favourite_organization(request):
    if request.session.get('user_auth'):
        email = request.session.get('user_auth')
        user = User.objects.get(email=email)
        favourite_organization = FavouriteOrganization.objects.filter(user=user)
        organization = [i.organizer for i in favourite_organization]
        for i in organization:
            i.image = "Images/" + str(i.photo)

        return render(request, 'webpages/view_favourite_organization.html',
                      {'organization': organization})
    else:
        raise Http404("You are not logged in")


def remove_favourite_organization(request, organization_id):
    email = request.session.get('user_auth')
    if email:
        try:
            organization = Organizer.objects.get(pk=organization_id)
            user = User.objects.get(email=email)
            try:
                favourite_organization = FavouriteOrganization.objects.get(user=user, organizer=organization)
                favourite_organization.delete()
                messages.success(request, "The organization " + organization.name +
                                 " was removed from favourite successfully.")
            except FavouriteOrganization.DoesNotExist:
                messages.warning(request, "The organization " + organization.name + " was not favourite.")

            return HttpResponseRedirect('/view-organization/')
        except Organizer.DoesNotExist or User.DoesNotExist:
            raise Http404("You are not logged in or organization is not registered.")

    else:
        raise Http404("You are not logged in")


def view_interest(request):
    email = request.session.get('user_auth')
    if email:

        user = User.objects.get(email=email)
        interest = Interest.objects.filter(user=user)
        interest = sorted(interest, key=lambda x: x.priority, reverse=True)
        for i in interest:
            i.image = "Images/" + str(i.category.photo)
        return render(request, 'webpages/view_interest.html', {'interest': interest})
    else:
        raise Http404("You are not logged in.")


def edit_event(request, event_id):
    organization_email = request.session.get('organization_auth')
    if not organization_email:
        raise Http404("You are not Logged in")
    if request.method == "POST":
        form = EditEvent(request.POST, request.FILES, event_id=event_id)
        if form.is_valid():
            try:
                event = Event.objects.get(pk=event_id)
                event.title = request.POST.get('title')
                event.description = request.POST.get('description')
                event.venue = request.POST.get('venue')
                event.start_time = request.POST.get('start_time')
                event.end_time = request.POST.get('end_time')
                event.category = Category.objects.get(pk=request.POST.get('category'))

                event.save()
                messages.success(request, "The event "+event.title+" was update successfully.")
            except Event.DoesNotExist:
                messages.success(request, "This event was not registered.")
            return redirect('/organization-event/')

    else:
        form = EditEvent(event_id=event_id)
    return render(request, 'webpages/edit_event.html', {'form': form})


def not_delete(request, types):
    if types == 'event':
        return redirect('/organization-event/')
    elif types == 'interest':
        return redirect('/view-interest/')
    elif types == 'calendar':
        return redirect('/view-calendar/')


def delete_event_confirm(request, event_id):
    if request.session.get('organization_auth'):
        event = Event.objects.get(pk=event_id)
        return render(request, 'webpages/delete_event_confirmation.html', {'event': event})

    else:
        raise Http404("You are not logged in")


def delete_event(request, event_id):
    if request.session.get('organization_auth'):
        try:
            event = Event.objects.get(pk=event_id)
            event.delete()
            messages.success(request, "The event " + event.title + " was deleted successfully.")
            return redirect('/organization-event/')
        except Event.DoesNotExist:
            raise Http404("This event is not registered")
    else:
        raise Http404("You are not logged in")


def edit_interest(request, interest_id):
    user_email = request.session.get('user_auth')
    if not user_email:
        raise Http404("You are not Logged in")
    if request.method == "POST":
        form = EditInterest(request.POST, interest_id=interest_id)
        if form.is_valid():
            try:
                interest = Interest.objects.get(pk=interest_id)
                interest.priority = request.POST.get('priority')

                interest.save()
                messages.success(request, "The interest "+interest.category.name+" was update successfully.")
            except Interest.DoesNotExist:
                messages.success(request, "This event was not registered.")
            return redirect('/view-interest/')

    else:
        form = EditInterest(interest_id=interest_id)
    return render(request, 'webpages/edit_interest.html', {'form': form})


def delete_interest_confirm(request, interest_id):
    if request.session.get('user_auth'):
        interest = Interest.objects.get(pk=interest_id)
        return render(request, 'webpages/delete_interest_confirmation.html', {'interest': interest})

    else:
        raise Http404("You are not logged in")


def delete_interest(request, interest_id):
    if request.session.get('user_auth'):
        try:
            interest = Interest.objects.get(pk=interest_id)
            interest.delete()
            messages.success(request, "The interest " + interest.category.name + " was deleted successfully.")
            return redirect('/view-interest/')
        except Event.DoesNotExist:
            raise Http404("This interest is not registered")
    else:
        raise Http404("You are not logged in")


def view_organization_event_by_user(request, organization_id):
    email = request.session.get('user_auth')
    if email:
        user = User.objects.get(email=email)
        organizer = Organizer.objects.get(pk=organization_id)
        if request.method == "POST":
            form = DateSearchEngine(request.POST)
            if form.is_valid():
                date = request.POST.get('search_date')
                event = Event.objects.filter(organizer=organizer, start_time__date=date)
                event = sorted(event, key=lambda x: x.register_date, reverse=True)

                my_calendar = Calendar.objects.filter(user=user).exclude(event=None)
                calendar = {}
                for i in my_calendar:
                    calendar[i.event.id] = True

                for i in event:
                    if not calendar.get(i.id):
                        calendar[i.id] = False

                return render(request, 'webpages/view_organization_event_by_user.html',
                              {'event': event, 'form': form, 'calendar': calendar, 'date': date, 'name': organizer.name})

            return render(request, 'webpages/view_organization_event_by_user.html',
                          {'form': form, 'date': None, 'name': organizer.name})
        else:
            form = DateSearchEngine()
            event = Event.objects.filter(organizer=organizer)
            event = sorted(event, key=lambda x: x.register_date, reverse=True)
            my_calendar = Calendar.objects.filter(user=user).exclude(event=None)
            calendar = {}
            for i in my_calendar:
                calendar[i.event.id] = True

            for i in event:
                if not calendar.get(i.id):
                    calendar[i.id] = False

            return render(request, 'webpages/view_organization_event_by_user.html',
                          {'event': event, 'form': form, 'calendar': calendar, 'date': None, 'name': organizer.name})

    else:
        raise Http404("You are not logged in.")


def view_favourite_category_events(request):
    email = request.session.get('user_auth')
    if email:
        user = User.objects.get(email=email)
        if request.method == "POST":
            form = DateSearchEngine(request.POST)
            if form.is_valid():
                date = request.POST.get('search_date')
                interest = Interest.objects.filter(user=user)
                event = []
                for i in interest:
                    my = Event.objects.filter(category=i.category, start_time__date=date)
                    for k in my:
                        event.append(k)
                # event = Event.objects.filter(start_time__date=date)
                event = sorted(event, key=lambda x: x.register_date, reverse=True)

                my_calendar = Calendar.objects.filter(user=user).exclude(event=None)
                calendar = {}
                for i in my_calendar:
                    calendar[i.event.id] = True

                for i in event:
                    if not calendar.get(i.id):
                        calendar[i.id] = False

                return render(request, 'webpages/view_favourite_category_events.html',
                              {'event': event, 'form': form, 'calendar': calendar, 'date': date})

            return render(request, 'webpages/view_favourite_category_events.html', {'form': form, 'date': None})
        else:
            form = DateSearchEngine()
            interest = Interest.objects.filter(user=user)
            event = []
            for i in interest:
                my = Event.objects.filter(category=i.category)
                for k in my:
                    event.append(k)
            event = sorted(event, key=lambda x: x.register_date, reverse=True)

            my_calendar = Calendar.objects.filter(user=user).exclude(event=None)
            calendar = {}
            for i in my_calendar:
                calendar[i.event.id] = True

            for i in event:
                if not calendar.get(i.id):
                    calendar[i.id] = False

            return render(request, 'webpages/view_favourite_category_events.html',
                          {'event': event, 'form': form,  'calendar': calendar, 'date': None})

    else:
        raise Http404("You are not logged in.")


def add_interest_category(request):
    email = request.session.get('user_auth')
    if not email:
        raise Http404("You are not Logged in")
    if request.method == "POST":
        form = AddInterestCategory(request.POST, user_email=email)
        if form.is_valid():
            user = User.objects.get(email=email)
            category = Category.objects.get(pk=request.POST.get('category'))
            priority = request.POST.get('priority')
            date = datetime.now().date()
            post = Interest(user=user, category=category, priority=priority, register_date=date)
            post.save()
            messages.success(request, "The category " + category.name + " was added to favourite successfully.")
            return redirect('/add-interest-category/')

    else:
        form = AddInterestCategory(user_email=email)
    return render(request, 'webpages/add_interest_category.html', {'form': form})


def view_calendar(request):
    email = request.session.get('user_auth')
    if email:
        user = User.objects.get(email=email)

        if request.method == "POST":
            form = DateSearchEngine(request.POST)
            if form.is_valid():
                date = request.POST.get('search_date')
                event = Calendar.objects.filter(user=user, event__start_time__date=date).order_by('register_date')
                return render(request, 'webpages/view_calendar.html', {'event': event, 'form': form, 'date': date})

            return render(request, 'webpages/view_calendar.html', {'form': form, 'date': None})
        else:
            form = DateSearchEngine()
            event = Calendar.objects.filter(user=user).order_by('register_date').reverse()

            return render(request, 'webpages/view_calendar.html', {'event': event, 'form': form, 'date': None})

    else:
        raise Http404("You are not logged in.")


def remove_from_calendar_confirm(request, calendar_id):
    email = request.session.get('user_auth')
    if email:
        try:
            calendar = Calendar.objects.get(pk=calendar_id)
            return render(request, 'webpages/remove_from_calendar_confirmation.html', {'calendar': calendar})
        except Calendar.DoesNotExist:
            messages.warning(request, "This event is not found in your calendar")

        return redirect('/view-calendar/')
    else:
        raise Http404("You are not logged in.")


def remove_from_calendar(request, calendar_id):
    email = request.session.get('user_auth')
    if email:

        try:
            calendar = Calendar.objects.get(pk=calendar_id)
            calendar.delete()
            messages.success(request, "The event "+calendar.title+" was removed from calendar successfully.")
        except Calendar.DoesNotExist:
            messages.warning(request, "This event is not found in your calendar")

        return redirect('/view-calendar/')
    else:
        raise Http404("You are not logged in.")


def add_calendar(request):
    email = request.session.get('user_auth')
    if email:
        if request.method == "POST":
            form = AddCalendar(request.POST)
            if form.is_valid():
                user = User.objects.get(email=email)
                date = datetime.now().date()
                title = request.POST.get('title')
                start_time = request.POST.get('start_time')
                end_time = request.POST.get('end_time')
                venue = request.POST.get('venue')
                try:
                    category = Category.objects.get(pk=request.POST.get('category'))
                except ValueError or Category.DoesNotExist:
                    category = None
                description = request.POST.get('description')
                post = Calendar(user=user, title=title, start_time=start_time, end_time=end_time, venue=venue,
                                category=category, description=description, register_date=date)
                post.save()
                messages.success(request, "The calendar "+title+" was added to calendar successfully.")
        else:
            form = AddCalendar()
        return render(request, 'webpages/add_calendar.html', {'form': form})

    else:
        raise Http404("You are not logged in.")


def email_confirmation(request, email, person):
    current_site = get_current_site(request)
    mail_subject = 'Activate your blog account.'
    message = render_to_string('webpages/acc_active_email.html', {
        'user': person,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(person.pk)).decode(),
        'email': urlsafe_base64_encode(force_bytes(person.email)).decode(),
        'token': account_activation_token.make_token(person),
    })
    to_email = email
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.send()
    # print( urlsafe_base64_encode(force_bytes(person.pk)).decode())
    messages.success(request, 'Please confirm your email address to complete the registration')


def activate(self, **kwargs):
    token = kwargs.get('token')
    uidb64 = kwargs.get('uidb64')
    encode_email = kwargs.get('email')
    try:
        email = urlsafe_base64_decode(encode_email).decode()
        uid = urlsafe_base64_decode(uidb64).decode()

        try:
            user = User.objects.get(pk=uid, email=email)

        except User.DoesNotExist:
            try:
                user = Organizer.objects.get(pk=uid, email=email)
            except Organizer.DoesNotExist:
                    user = None

    except(TypeError, ValueError, OverflowError):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = 'active'
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


