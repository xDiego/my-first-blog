from django.conf.urls import url 
from . import views

urlpatterns = [
    url(r'^$', views.main_page, name='main_page'),
    url(r'^blogs/(?P<pk>[1-9]+)/$', views.post_list1, name='post_list1'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^post_list/', views.post_list, name='post_list'),
    url(r'^post/(?P<pk>[0-9]+)/$', views.post_detail, name='post_detail'),
    url(r'^post/new/$', views.post_new, name='post_new'),
    url(r'^post/(?P<pk>[0-9]+)/edit/$', views.post_edit, name='post_edit'),
    url(r'^drafts/$', views.post_draft_list, name='post_draft_list'),
    url(r'^post/(?P<pk>[0-9]+)/publish/$', views.post_publish, name='post_publish'),
    url(r'^post/(?P<pk>[0-9]+)/remove/$',views.post_remove, name='post_remove'),
    url(r'post/(?P<pk>[0-9]+)/comment/$', views.add_comment_to_post, name='add_comment_to_post'),
    url(r'^comment/(?P<pk>[0-9]+)/approve/$', views.comment_approve, name='comment_approve'),
    url(r'^comment/(?P<pk>[0-9]+)/remove/$', views.comment_remove, name='comment_remove'),
    url(r'^register/$', views.register, name='register'),
    url(r'^settings/$', views.settings_page, name='settings_page'),
    url(r'^user_settings/$', views.settings_page, name='settings_page'),
    url(r'^blog_settings/$', views.blog_settings, name='blog_settings'),
    url(r'blog_settings/(?P<pk>[1-9]+)/$', views.blog_edit, name='blog_edit'),
    url(r'^blog_settings/create_blog/$', views.create_blog, name='create_blog'),
]
