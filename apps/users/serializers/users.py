from rest_framework import serializers
from django.contrib.auth import get_user_model
import re
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError


class UserListSerializer(serializers.ModelSerializer):
    is_deleted = serializers.ReadOnlyField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'birth_date', 'avatar', 'bookings', 'listings',
                  'phone', 'last_login', 'date_joined', 'updated_at', 'is_deleted', 'deleted_at']
        read_only_fields = ['id', 'updated_at', 'deleted_at', 'date_joined', 'bookings', 'listings', 'last_login']

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    re_password = serializers.CharField(min_length=8, max_length=128, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'first_name', 'last_name', 'birth_date', 'avatar',
                  'phone', 'last_login', 'password', 're_password', 'deleted_at']
        read_only_fields = ['id', 'deleted_at', 'last_login']

    def validate_phone(self, value):
        if not value or value.strip() == '':
            return None
        if not re.match(r'^\+\d{10,75}$', value):
            raise serializers.ValidationError(_('The phone number must consist of 10-75 symbols in total and start from + symbol!!\n'
                                              'Example: +3423234455323'))
        return value

    def validate_email(self, value):
        if get_user_model().all_objects.filter(email=value).exclude(id__in=[self.instance.pk] if self.instance else []).exists():
            raise serializers.ValidationError(_('This email already exists!!'))
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        if self.instance is None or 'password' in attrs or 're_password' in attrs:
            if not attrs.get('password') or not attrs.get('re_password'):
                raise serializers.ValidationError({'password': 'Password fields are required for registration!!'})
            if attrs.get('password') != attrs.get('re_password'):
                raise DRFValidationError({'re_password': 'Passwords do not match!!'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('re_password', None)
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('re_password', None)
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

