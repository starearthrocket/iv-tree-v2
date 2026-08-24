from django.contrib import admin

from .models import ProgressUpdate, TreeReport


admin.site.register(TreeReport)
admin.site.register(ProgressUpdate)