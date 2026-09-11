from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe

User = get_user_model()


@admin.register(User)
class Admin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'get_avatar',
        'first_name',
        'last_name',
        'birth_date',
        'phone',
        'is_active',
        'is_staff',
        'date_joined',
        'updated_at',
        'show_is_deleted'
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    @admin.display(description='Avatar')
    def get_avatar(self, user):
        if user.avatar:
            return mark_safe(f'<img src="{user.avatar.url}" style="max-height: 40px; border-radius: 50%;" />')
        return '-No photo-'

    @admin.display(boolean=True, description='Deleted?')
    def show_is_deleted(self, user):
        return user.is_deleted