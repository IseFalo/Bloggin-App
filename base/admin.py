from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(Notification)
admin.site.register(Category)
admin.site.register(Series)
admin.site.register(Organization)
admin.site.register(Product)