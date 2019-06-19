from django.contrib import admin
from authentication.models import *

admin.site.register([Usertype, Topic, Messages, SentFiles,SentKey])
