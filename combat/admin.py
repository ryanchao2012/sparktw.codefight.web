from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from combat.models import (
    Contestant, Quiz, Snippet
)


# Register your models here.
class ContestantInline(admin.StackedInline):
    model = Contestant
    fk_name = 'user'


class ExtendUserAdmin(UserAdmin):
    inlines = [ContestantInline, ]


class ContestantAdmin(admin.ModelAdmin):
    list_display = ('nickname', )


class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'status',)
    list_editable = ('status',)
    readonly_fields = ('slug',)


class SnippetAdmin(admin.ModelAdmin):
    list_display = ('contestant', 'quiz', 'language', 'status', 'last_run')
    # readonly_fields = ('script',)


admin.site.register(Contestant, ContestantAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Snippet, SnippetAdmin)

admin.site.unregister(User)
admin.site.register(User, ExtendUserAdmin)
