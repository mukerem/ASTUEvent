"""bookstore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.homepage, name='home'),
    path('homepage/', views.homepage, name='home'),
    path('user-register/', views.user_register, name='user_register'),
    path('organization-register/', views.organization_register, name='organization_register'),
    path('login/', views.login, name='login'),
    path('notification/', views.notification, name='notification'),
    path('logout/<role>/', views.logout, name='logout'),
    path('add-to-calendar/<event_id>/<types>/', views.add_to_calendar, name='addToCalendar'),
    path('user-profile/', views.view_user_profile, name='user_profile'),
    path('change-password/<role>/', views.change_password, name='ChangePassword'),
    path('organization-event/', views.view_organization_event, name='organization_event'),
    path('organization-profile/', views.view_organization_profile, name='organization_profile'),
    path('add-event/', views.add_event, name='add_event'),
    path('add-category/', views.add_category, name='add_category'),
    path('view-category/', views.view_category, name='view_category'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('view-event/', views.view_event, name='view_event'),
    path('view-organization/', views.view_organization, name='view_organization'),
    path('add-favourite/<organization_id>/', views.add_favourite_organization, name='addFavouriteStore'),
    path('favourite-organization/', views.view_favourite_organization, name='favourite_organization'),
    path('view-organization-event-by-user/<organization_id>/', views.view_organization_event_by_user,
         name='viewOrganizationEvent'),

    path('remove-favourite/<organization_id>/', views.remove_favourite_organization, name='removeFavouriteStore'),
    path('view-interest/', views.view_interest, name='view_interest'),
    path('edit-event/<event_id>/', views.edit_event, name='editEvent'),
    path('delete-event-confirm/<event_id>/', views.delete_event_confirm, name='deleteEventConfirm'),
    path('delete-event/<event_id>/', views.delete_event, name='deleteEvent'),
    path('notDelete/<types>/', views.not_delete, name='NotDelete'),
    path('view-interest/', views.view_interest, name='view_interest'),
    path('edit-interest/<interest_id>/', views.edit_interest, name='editInterest'),
    path('delete-interest-confirm/<interest_id>/', views.delete_interest_confirm, name='deleteInterestConfirm'),
    path('delete-interest/<interest_id>/', views.delete_interest, name='deleteInterest'),
    path('favourite-category-events/', views.view_favourite_category_events, name='view_favourite_category_events'),
    path('add-interest-category/', views.add_interest_category, name='add_interest_category'),
    path('view-calendar/', views.view_calendar, name='view_calendar'),
    path('add-calendar/', views.add_calendar, name='add_calendar'),
    path('remove-from-calendar-confirm/<calendar_id>/', views.remove_from_calendar_confirm,
         name='removeFromCalendarConfirm'),
    path('remove-from-calendar/<calendar_id>/', views.remove_from_calendar, name='removeFromCalendar'),
    path('activate/<uidb64>/<email>/<token>/', views.activate, name='activate'),

]

