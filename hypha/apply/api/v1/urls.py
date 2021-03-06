from django.urls import path
from rest_framework_nested import routers

from hypha.apply.api.v1.determination.views import SubmissionDeterminationViewSet
from hypha.apply.api.v1.review.views import SubmissionReviewViewSet
from hypha.apply.api.v1.screening.views import (
    ScreeningStatusViewSet,
    SubmissionScreeningStatusViewSet,
)

from .views import (
    CommentViewSet,
    CurrentUser,
    RoundViewSet,
    SubmissionActionViewSet,
    SubmissionCommentViewSet,
    SubmissionViewSet,
)

app_name = 'v1'


router = routers.SimpleRouter()
router.register(r'submissions', SubmissionViewSet, basename='submissions')
router.register(r'comments', CommentViewSet, basename='comments')
router.register(r'rounds', RoundViewSet, basename='rounds')
router.register(r'screening_statuses', ScreeningStatusViewSet, basename='screenings')

submission_router = routers.NestedSimpleRouter(router, r'submissions', lookup='submission')
submission_router.register(r'actions', SubmissionActionViewSet, basename='submission-actions')
submission_router.register(r'comments', SubmissionCommentViewSet, basename='submission-comments')
submission_router.register(r'reviews', SubmissionReviewViewSet, basename='reviews')
submission_router.register(r'determinations', SubmissionDeterminationViewSet, basename='determinations')
submission_router.register(r'screening_statuses', SubmissionScreeningStatusViewSet, basename='submission-screening_statuses')

urlpatterns = [
    path('user/', CurrentUser.as_view(), name='user'),
]

urlpatterns = router.urls + submission_router.urls + urlpatterns
