from django.urls import path
from task import views

urlpatterns = [
    path('', views.inicio_jogo_view, name='home'),  # Página inicial
    path('game/', views.game_view, name='game'),  # Página do jogo
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),  # Leaderboard
    path('endgame/', views.endgame_view, name='endgame'),
]

