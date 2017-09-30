from django.shortcuts import render
from combat.utils import AnnounceData
from .models import Announcement
# Create your views here.


def billboard(request):
    announces = Announcement.objects.all().order_by('-modified')
    if not request.user.is_staff:
        announces = announces.filter(status='published')

    anndata = []
    for ann in announces:
        anndata.append(
            AnnounceData(
                title=ann.title,
                body=ann.body,
                manager=ann.manager.username,
                created=ann.created.timestamp(),
                modified=ann.modified.timestamp(),
                is_draft=(ann.status != 'published')
            )
        )

    return render(request, 'billboard.html', {'anndata': anndata})
