from django.urls import path


from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("listings/<int:id>", views.listing_page, name="listing_page"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path('upload', views.upload, name='upload'),
    path('watchlist', views.watchlist, name='watchlist'),
    path('bid/<int:id>', views.bid, name='bid'),
    path('add_comment/<int:id>', views.add_comment, name='add_comment'),
    path('add_watchlist/<int:id>', views.add_watchlist, name='add_watchlist'),

    path('check-session/', views.check_session, name='check_session'),
]
