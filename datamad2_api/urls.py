from django.urls import path, include
from rest_framework import routers
from datamad2_api import views

router = routers.DefaultRouter()
router.register(r'grants', views.GrantViewSet)
router.register(r'importedgrants', views.ImportedGrantViewSet)
# router.register(r'users', views.UserViewSet)
# router.register(r'permission', views.PermissionViewSet)
router.register(r'datacenters', views.DataCentreViewSet, basename="datacenters")
router.register(r'datacentres', views.DataCentreViewSet, basename="datacentres")
router.register(r'subtasks', views.SubtaskViewSet)

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('', include(router.urls)),
]
