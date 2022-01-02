from django.contrib import admin
from .models import User, Organizer, Category, Event, Interest, Calendar, FavouriteOrganization,Notification

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    fields = ('name', 'middle_name', 'last_name', 'phone', 'email', 'year', 'department', 'password',
              'sex', 'image_tag', 'photo', 'is_active', 'register_date')
    readonly_fields = ('image_tag',)


class OrganizerAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'phone', 'email', 'password', 'image_tag', 'photo', 'is_active', 'register_date')
    readonly_fields = ('image_tag',)


class CategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'image_tag', 'photo')
    readonly_fields = ('image_tag',)


admin.site.register(User, UserAdmin)
admin.site.register(Organizer, OrganizerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Interest)
admin.site.register(Event)
admin.site.register(Calendar)
admin.site.register(FavouriteOrganization)
admin.site.register(Notification)