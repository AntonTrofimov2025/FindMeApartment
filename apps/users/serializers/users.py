from rest_framework import serializers
from django.contrib.auth import get_user_model
import re
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


class ValidatePhoneMixin:
    """
    Reusable validation mixin encapsulating strict E.164 phone syntax logic.
    """
    def validate_phone(self, value):
        if not value or value.strip() == '':
            return None
        if not re.match(r'^\+\d{10,75}$', value):
            raise serializers.ValidationError(_('The phone number must consist of 10-75 symbols in total and start from + symbol!!\n'
                                              'Example: +3423234455323'))
        return value

class UserListSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for full user profile summaries.

    Exposes all non-sensitive user metadata, including relation counters for
    associated listings and bookings. Used for rendering accounts in directories
    and the personal profile dashboard.
    """
    is_deleted = serializers.BooleanField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'birth_date', 'avatar', 'bookings', 'listings',
                  'phone', 'last_login', 'date_joined', 'updated_at', 'is_deleted', 'deleted_at']
        read_only_fields = ['id', 'updated_at', 'deleted_at', 'date_joined', 'bookings', 'listings', 'last_login']

class RegisterUserSerializer(ValidatePhoneMixin, serializers.ModelSerializer):
    """
    Write/Update serializer for user registration and profile modifications.

    Manages account creation fields and partial profile updates (`PATCH`).
    Enforces password complexity match controls on initial registration.

    Validation Rules:
        - phone: Enforces strict E.164 syntax checks (`+` symbol followed by 10-75 digits).
          Normalizes empty strings or white spaces directly to `None` in the database.
        - email: Implements custom global unique constraints, checking inputs against
          both active and soft-deleted records to prevent email duplication.
        - password: Pipes raw text inputs directly into Django's core AUTH_PASSWORD_VALIDATORS.
    """
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    re_password = serializers.CharField(min_length=8, max_length=128, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'first_name', 'last_name', 'birth_date', 'avatar',
                  'phone', 'password', 're_password']

    def validate_email(self, value):
        if get_user_model().all_objects.filter(email=value).exclude(id__in=[self.instance.pk] if self.instance else []).exists():
            raise serializers.ValidationError(_('This email already exists!!'))
        return value

    def validate_password(self, value):
        try:
            password_validation.validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        if not self.instance or 'password' in attrs or 're_password' in attrs:
            if not attrs.get('password') or not attrs.get('re_password'):
                raise serializers.ValidationError({'password': 'Password fields are required for registration!!'})
            if attrs.get('password') != attrs.get('re_password'):
                raise DRFValidationError({'re_password': 'Passwords do not match!!'})
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop('re_password', None)
        return get_user_model().objects.create_user(**validated_data)

class ProfileUpdateSerializer(ValidatePhoneMixin, serializers.ModelSerializer):
    """
    Dedicated serializer for safe profile mutations.

    Strictly excludes sensitive credential tokens (password, email) to eliminate
    unauthorized background account takeover and session hijacking security holes.
    """

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name', 'birth_date', 'avatar', 'phone']

    def update(self, instance, validated_data):
        avatar = validated_data.pop('avatar', None)
        if avatar is not None:
            if instance.avatar:
                instance.avatar.delete(save=False)
            instance.avatar = avatar

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for secure password mutation workflows.
    Requires verification of the historic credential sequence before injecting new salts.
    """
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, min_length=8, max_length=128, required=True)
    re_new_password = serializers.CharField(write_only=True, min_length=8, max_length=128, required=True)
    refresh = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password verification failed! Please try again.")
        return value

    def validate_new_password(self, value):
        """
        Enforces strict built-in Django password validators (length, common passwords, attributes).
        """
        user = self.context.get('request').user
        try:
            validate_password(value, user=user)
        except ValidationError as e:
            e = e.message_dict if hasattr(e, 'message_dict') else e.messages
            raise serializers.ValidationError(e)
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['re_new_password']:
            raise serializers.ValidationError({"re_new_password": "New passwords do not match!!"})

        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError(_("Authentication context missing."))

        user = request.user
        refresh_token = attrs.get('refresh')

        try:
            refresh = RefreshToken(refresh_token)
            token_user_id = refresh.get('user_id')
            if str(token_user_id) != str(user.id):
                raise serializers.ValidationError({
                    'refresh': _('Security breach: Provided refresh token does not belong to your account session!')
                })
        except TokenError:
            raise serializers.ValidationError({
                'refresh': _('Provided refresh token is invalid or already expired.')
            })

        return super().validate(attrs)
