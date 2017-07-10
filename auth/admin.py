from django.contrib import admin
from auth.models import RepeatUserName
# Register your models here.


class RepeatUserNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'count')


admin.site.register(RepeatUserName, RepeatUserNameAdmin)
