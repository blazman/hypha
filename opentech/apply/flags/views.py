import json

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views import View

from opentech.apply.funds.models import ApplicationSubmission

from .models import Flag


@method_decorator(login_required, name='dispatch')
class FlagSubmissionCreateView(View):
    model = Flag

    def post(self, request, type, submission_pk):
        if not request.is_ajax():
            return HttpResponseNotAllowed()

        submission_type = ContentType.objects.get_for_model(ApplicationSubmission)
        # Trying to get a flag from the table, or create a new one
        flag, created = self.model.objects.get_or_create(user=request.user, target_object_id=submission_pk, target_content_type=submission_type, type=type)
        # If no new flag has been created,
        # Then we believe that the request was to delete the flag.
        if not created:
            flag.delete()

        return HttpResponse(
            json.dumps({
                "result": created
            }),
            content_type="application/json"
        )