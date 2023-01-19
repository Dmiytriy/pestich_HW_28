from django.contrib import admin

from ads.models import *
from users.models import *

admin.site.register(Ad)
admin.site.register(Category)
admin.site.register(Location)
admin.site.register(User)

