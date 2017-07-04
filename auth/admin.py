from django.contrib import admin
from auth.models import RepeatUser
# Register your models here.


class RepeatUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'count')


admin.site.register(RepeatUser, RepeatUserAdmin)
