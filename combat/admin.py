from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from combat.models import (
    Contestant, Quiz, Snippet, Answer
)


# Register your models here.
class ContestantInline(admin.StackedInline):
    model = Contestant
    fk_name = 'user'


class ExtendUserAdmin(UserAdmin):
    inlines = [ContestantInline, ]


class ContestantAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'valid_name')
    search_fields = ['nickname', 'uid']


class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'status',)
    list_editable = ('status',)
    readonly_fields = ('slug',)
    search_fields = ['title', 'uid']


class SnippetAdmin(admin.ModelAdmin):
    list_display = ('contestant', 'quiz', 'language', 'created', 'last_run', 'run_count', 'is_running')
    list_filter = ('language', 'status')
    list_editable = ('is_running',)
    search_fields = ['contestant__nickname', 'uid', 'quiz__title']
    # readonly_fields = ('script',)


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('contestant', 'quiz', 'language', 'elapsed', 'created', 'last_update')
    list_filter = ('language',)
    search_fields = ['contestant__nickname', 'quiz__title']

admin.site.register(Contestant, ContestantAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Snippet, SnippetAdmin)
admin.site.register(Answer, AnswerAdmin)

admin.site.unregister(User)
admin.site.register(User, ExtendUserAdmin)
