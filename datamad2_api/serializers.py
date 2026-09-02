from datamad2.models import Grant, ImportedGrant, User, DataCentre, JIRASubtask, GithubSubtask
from rest_framework import serializers
from django.contrib.auth.models import Permission


class GrantSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Grant
        fields = '__all__'


class ImportedGrantSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ImportedGrant
        fields = '__all__'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class PermissionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class DataCentreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataCentre
        fields = '__all__'


class JIRASubtaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = JIRASubtask
        fields = '__all__'


class GithubSubtaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GithubSubtask
        fields = '__all__'