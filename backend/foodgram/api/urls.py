from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

app_name = 'api'
router = DefaultRouter()

# router_v1.register('posts', PostViewSet)
# router_v1.register('groups', GroupViewSet)
# router_v1.register(r'follow', LightFollowViewSet, basename='follower')
# router_v1.register('posts/(?P<post_id>\\d+)/comments',
#                    CommentViewSet, basename='comments')


urlpatterns = [
    path('', include(router.urls)),
    # path('', include('djoser.urls')),
    # re_path(r'^auth/', include('djoser.urls.authtoken')),

]
