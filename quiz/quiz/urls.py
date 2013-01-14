from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

handler500 = 'quizform.views.error'
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'quiz.views.home', name='home'),
    # url(r'^quiz/', include('quiz.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^$', 'quizform.views.handle'),
    url(r'^(?P<instructor>[^/]+)/(?P<classname>[^/]+)/(?P<quiz>[^/]*)/?$',
            'quizform.views.handle_complicated'),
    url(r'^dashboard/(?P<instructor>[^/]+)/(?P<classname>[^/]+)/(?P<quiz>[^/]+)/$',
            'quizform.views.dashboard'),
    url(r'^dashboard/(?P<instructor>[^/]+)/(?P<classname>[^/]+)/$',
            'quizform.views.dashboard'),
    url(r'^dashboard/(?P<instructor>[^/]+)/$', 'quizform.views.dashboard'),
    url(r'^dashboard/$', 'quizform.views.dashboard'),
)
