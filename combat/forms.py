from django import forms
from combat.models import Snippet
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.forms.widgets import Select
from django.utils import timezone
# from django.forms.widgets import TextInput


class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        exclude = ['script', 'run_count']

    def save(self, commit=True):
        instance = super(SnippetForm, self).save(commit=False)

        if self.cleaned_data.get('body', '') != self.initial.get('body', ''):
            path = 'snippet/{0}/{1}/{2}.{3}'.format(
                instance.contestant.valid_name(),
                instance.quiz.valid_name(),
                instance.valid_name(),
                'scala' if 'scala' in instance.language else 'py'
            )
            default_storage.delete(path)
            instance.script = default_storage.save(path, ContentFile(instance.body))
            instance.run_count += 1
        instance.is_running = True
        instance.last_run = timezone.now()
        if commit:
            instance.save()

        return instance


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = ('language',)
        widgets = {
            'language': Select(attrs={'class': 'selectpicker', 'data-width': '120px'}),
        }
