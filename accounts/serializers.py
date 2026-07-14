from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('phone', 'password', 'password_confirm', 'gender', 'goal', 'activity_level')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "پسوردها با هم مطابقت ندارند."})
        return attrs

    def create(self, validated_data):
        # حذف پسورد تایید قبل از ساخت کاربر
        validated_data.pop('password_confirm')
        
        # ساخت کاربر با پسورد هش‌شده (امن)
        user = User.objects.create_user(
            phone=validated_data['phone'],
            password=validated_data['password'],
            gender=validated_data.get('gender'),
            goal=validated_data.get('goal', 'maintain'),
            activity_level=validated_data.get('activity_level', 'moderate')
        )
        return user