from datamad2.models import Grant, ImportedGrant, User, DataCentre, JIRASubtask, GithubSubtask
from rest_framework import viewsets
from datamad2_api.serializers import GrantSerializer, ImportedGrantSerializer, \
    UserSerializer, PermissionSerializer, DataCentreSerializer, JIRASubtaskSerializer, GithubSubtaskSerializer
from django.contrib.auth.models import Permission

class GrantViewSet(viewsets.ModelViewSet):
    # everything in triple quotes is seen by the user
    """
    API endpoint that allows grants to be viewed or edited.
    """
    queryset = Grant.objects.all()
    serializer_class = GrantSerializer


class ImportedGrantViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows grants to be viewed or edited.
    """
    queryset = ImportedGrant.objects.all()
    serializer_class = ImportedGrantSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows grants to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PermissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows permissions to be viewed or edited.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class DataCentreViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows datacentres to be viewed or edited.
    """
    queryset = DataCentre.objects.all()
    serializer_class = DataCentreSerializer


class JIRASubtaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows sub-tasks to be viewed or edited.
    """
    queryset = JIRASubtask.objects.all()
    serializer_class = JIRASubtaskSerializer

class GithubSubtaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows sub-tasks to be viewed or edited.
    """
    queryset = GithubSubtask.objects.all()
    serializer_class = GithubSubtaskSerializer
