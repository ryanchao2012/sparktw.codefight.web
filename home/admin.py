from django.contrib import admin

# Register your models here.
from ghoster.admin import GhosterAdmin
from .models import Announcement


class AnnouncementAdmin(GhosterAdmin):
    markdown_field = 'body'
    title_field = 'title'

    # other stuff
    list_display = ('title', 'manager', 'status', 'created', 'modified')
    list_editable = ('status',)
    # list_filter = ...

admin.site.register(Announcement, AnnouncementAdmin)
