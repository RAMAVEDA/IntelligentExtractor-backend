from django.contrib import admin
from .models import File, Document, User, Field
# Register your models here.

admin.site.register([File, Document, User, Field])
