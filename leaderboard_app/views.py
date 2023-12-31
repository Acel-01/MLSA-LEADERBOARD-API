import requests
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from leaderboard_app.models import Submit
from leaderboard_app.serializers import (
    LeaderboardSerializer,
    SubmitErrorSerializer,
    SubmitSerializer,
)
from mlsa_leaderboard.settings import leaderboard_name, redis_mlsa_leaderboard
from users.serializers import UserSerializer


class SubmitCreateView(APIView):
    """
    Allows participant submit a pull request
    """

    serializer_class = SubmitSerializer
    lookup_field = "uuid"

    @extend_schema(
        request=serializer_class,
        responses={
            200: OpenApiResponse(
                response=SubmitSerializer,
                description="Pull Request submitted successfully",
            ),
            400: OpenApiResponse(
                response=SubmitErrorSerializer,
                description="Validation Error",
            ),
        },
        tags=["Leaderboard"],
        description="Submit a Pull Request",
    )
    def post(self, request):
        try:
            # Remove trailing slash do that all pr_link entries are uniform
            if request.data.get("pr_link")[-1] == "/":
                request.data["pr_link"] = request.data["pr_link"][:-1]

            serializer = self.serializer_class(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)

            user_url = serializer.initial_data.get("pr_link")
            list_url = user_url.split("/")

            if (
                list_url[0] != "https:"
                or list_url[2] != "github.com"
                or list_url[5] != "pull"
            ):
                raise serializers.ValidationError({"pr_link": ["This link is invalid"]})

            if Submit.objects.filter(user=request.user, pr_link=user_url):
                raise serializers.ValidationError(
                    {"pr_link": ["You have submitted this PR before"]}
                )

            # https://api.github.com/repos/OWNER/REPO/pulls/PULL_NUMBER
            api_url = f"https://api.github.com/repos/{list_url[3]}/{list_url[4]}/pulls/{list_url[6]}"
            r = requests.get(api_url)

            if r.status_code == 404:
                raise serializers.ValidationError(
                    {
                        "pr_link": [
                            "Invalid! This PR is from a private repository or it does not exist."
                        ]
                    }
                )

            if "hacktoberfest" not in r.json().get("base").get("repo").get("topics"):
                raise serializers.ValidationError(
                    {
                        "pr_link": [
                            "This repository is not participating in Hacktoberfest"
                        ]
                    }
                )

            if self.request.user.username != r.json().get("user").get("login"):
                raise serializers.ValidationError(
                    {
                        "pr_link": [
                            "Your Github username does not match this Pull Request"
                        ]
                    }
                )

            if "2023-10-01T00:00:00Z" > r.json().get("created_at"):
                raise serializers.ValidationError(
                    {
                        "pr_link": [
                            "This Pull Request was created before October 1st, 2023"
                        ]
                    }
                )

            # https://api.github.com/repos/OWNER/REPO/pulls/PULL_NUMBER/merge
            api_url = f"https://api.github.com/repos/{list_url[3]}/{list_url[4]}/pulls/{list_url[6]}/merge"
            r = requests.get(api_url)

            if r.status_code == 204:
                # PR was merged
                points = 4
            elif r.status_code == 404:
                # PR was not merged
                points = 2

            request.user.total_points += points

            # Add or Update this leaders score on the leaderboard
            redis_mlsa_leaderboard.rank_member_in(
                leaderboard_name=leaderboard_name,
                member=request.user.username,
                score=request.user.total_points,
            )

            request.user.save()
            serializer.save(points=points, user=self.request.user)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        except IndexError:
            raise serializers.ValidationError({"pr_link": ["This link is invalid"]})


class LeaderboardView(APIView):
    permission_classes = []
    serializer_class = LeaderboardSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="starting_rank",
                description="Filter by position",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="ending_rank",
                description="Filter by position",
                required=False,
                type=str,
            ),
        ],
        request=serializer_class,
        responses={
            200: OpenApiResponse(
                response=LeaderboardSerializer,
                description="Leaders fetched successfully",
            ),
        },
        tags=["Leaderboard"],
        description="List of the current top (20) participants",
    )
    def get(self, request):
        starting_rank = request.GET.get("starting_rank", 1)
        ending_rank = request.GET.get("ending_rank", 20)

        leaders = redis_mlsa_leaderboard.members_from_rank_range_in(
            leaderboard_name=leaderboard_name,
            starting_rank=int(starting_rank),
            ending_rank=int(ending_rank),
        )

        return Response(leaders)


class MyRankView(APIView):
    serializer_class = UserSerializer
    lookup_field = "uuid"

    @extend_schema(
        request=serializer_class,
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description="Score and Rank fetched successfully",
            ),
        },
        tags=["Leaderboard"],
        description="Score and Rank, as well as other details of the logged in user",
    )
    def get(self, request):
        user_obj = request.user
        serializer = self.serializer_class(user_obj, context={"request": request})

        score_and_rank = redis_mlsa_leaderboard.score_and_rank_for_in(
            leaderboard_name=leaderboard_name, member=request.user.username
        )
        data = serializer.data
        data["rank"] = score_and_rank.get("rank")
        return Response(data=data, status=status.HTTP_200_OK)
