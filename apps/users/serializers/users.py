from rest_framework import serializers
from django.contrib.auth import get_user_model
import re


class UserSerializer(serializers.ModelSerializer):
    is_deleted = serializers.ReadOnlyField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'birth_date',
                  'phone', 'last_login', 'date_joined', 'updated_at', 'is_deleted', 'deleted_at']
        read_only_fields = ['id', 'updated_at', 'created_at', 'updated_at', 'deleted_at', 'date_joined']

    def validate_phone(self, value):
        if not re.match(r'^\+\d{10,14}$', value):
            raise serializers.ValidationError('The phone number must consist of 10-15 symbols in total and start from + symbol!!\n'
                                              'Example: +3423234455323')
        return value

    def validate_email(self, value):
        if get_user_model().objects.filter(email=value).exclude(id__in=[self.instance.pk] if self.instance else []).exists():
            raise serializers.ValidationError('This email already exists!!')
        return value

