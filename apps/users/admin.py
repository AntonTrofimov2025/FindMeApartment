from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

User = get_user_model()


@admin.register(User)
class Admin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'get_avatar', 'first_name', 'last_name', 'birth_date',
        'phone', 'is_active', 'is_staff', 'last_login', 'date_joined', 'updated_at', 'show_is_deleted'
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    @admin.display(description=_('Avatar'))
    def get_avatar(self, user):
        if user.avatar:
            return mark_safe(f'<img src="{user.avatar.url}" style="max-height: 40px; border-radius: 50%;" />')
        return mark_safe('<span style="color: #999; font-style: italic;">- No photo -</span>')

    @admin.display(boolean=True, description=_('Deleted?'))
    def show_is_deleted(self, user):
        return user.is_deleted

    def get_queryset(self, request):
        return User.all_objects.get_queryset()

