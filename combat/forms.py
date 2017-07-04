from django import forms
from combat.models import Snippet
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.forms.widgets import Select, Textarea
# from django.forms.widgets import TextInput


class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        exclude = ['script', 'run_count']

    def save(self, commit=True):
        instance = super(SnippetForm, self).save(commit=False)

        ext = 'py'
        if 'scala' in instance.language:
            ext = 'scala'
        path = 'snippet/{0}/{1}/{2}.{3}'.format(
            instance.contestant.user.username, instance.quiz.slug, 'answer', ext
        )
        default_storage.delete(path)
        instance.script = default_storage.save(path, ContentFile(instance.body))
        instance.run_count += 1
        if commit:
            instance.save()

        return instance


class ClientSnippetForm(SnippetForm):
    class Meta:
        model = Snippet
        fields = ('body', 'language')
        widgets = {
            'language': Select(attrs={'class': 'selectpicker', 'data-width': '120px'}),
            'body': Textarea(attrs={'hidden': "true"}),
        }
