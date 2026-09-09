from rest_framework import serializers
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'birth_date',
                  'phone', 'last_login', 'date_joined', 'updated_at', 'is_deleted', 'deleted_at']
        read_only_fields = ['updated_at', 'deleted_at', 'date_joined']

