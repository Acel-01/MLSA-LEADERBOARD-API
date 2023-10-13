from django.urls import path

from leaderboard_app.views import LeaderboardView, SubmitCreateView

urlpatterns = [
    path("submit/", SubmitCreateView.as_view(), name="submit-pr"),
    path("", LeaderboardView.as_view(), name="list-leaderboard"),
]
