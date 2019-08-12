from io import BytesIO

from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase

from opentech.apply.users.tests.factories import (
    ApproverFactory,
    ReviewerFactory,
    StaffFactory,
    SuperUserFactory,
    UserFactory,
)
from opentech.apply.utils.testing.tests import BaseViewTestCase

from ..forms import SetPendingForm
from ..views import ProjectDetailView
from .factories import (
    DocumentCategoryFactory,
    PacketFileFactory,
    ProjectFactory,
)


class TestCreateApprovalView(BaseViewTestCase):
    base_view_name = 'detail'
    url_name = 'funds:projects:{}'
    user_factory = StaffFactory

    def get_kwargs(self, instance):
        return {'pk': instance.id}

    def test_creating_an_approval_happy_path(self):
        project = ProjectFactory()
        self.assertEqual(project.approvals.count(), 0)

        response = self.post_page(project, {'form-submitted-add_approval_form': '', 'by': self.user.id})
        self.assertEqual(response.status_code, 200)

        project.refresh_from_db()
        approval = project.approvals.first()

        self.assertEqual(project.approvals.count(), 1)
        self.assertFalse(project.is_locked)
        self.assertEqual(project.status, 'contracting')

        self.assertEqual(approval.project_id, project.pk)


class TestProjectDetailView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.project = ProjectFactory()

    def test_reviewer_does_not_have_access(self):
        request = self.factory.get('/projects/1/')
        request.user = ReviewerFactory()

        response = ProjectDetailView.as_view()(request, pk=self.project.pk)
        self.assertEqual(response.status_code, 403)

    def test_staff_user_has_access(self):
        request = self.factory.get('/projects/1/')
        request.user = StaffFactory()

        response = ProjectDetailView.as_view()(request, pk=self.project.pk)
        self.assertEqual(response.status_code, 200)

    def test_super_user_has_access(self):
        request = self.factory.get('/projects/1/')
        request.user = SuperUserFactory()

        response = ProjectDetailView.as_view()(request, pk=self.project.pk)
        self.assertEqual(response.status_code, 200)

    def test_user_does_not_have_access(self):
        request = self.factory.get('/projects/1/')
        request.user = UserFactory()

        with self.assertRaises(PermissionDenied):
            ProjectDetailView.as_view()(request, pk=self.project.pk)

    def test_owner_has_access(self):
        owner = UserFactory()
        request = self.factory.get('/projects/1/')
        request.user = owner
        project = ProjectFactory(user=owner)

        response = ProjectDetailView.as_view()(request, pk=project.pk)
        self.assertEqual(response.status_code, 200)


class TestRemoveDocumentView(BaseViewTestCase):
    base_view_name = 'detail'
    url_name = 'funds:projects:{}'
    user_factory = StaffFactory

    def get_kwargs(self, instance):
        return {'pk': instance.id}

    def test_remove_document(self):
        project = ProjectFactory()
        document = PacketFileFactory()

        response = self.post_page(project, {
            'form-submitted-remove_document_form': '',
            'id': document.id,
        })
        project.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(document.pk, project.packet_files.values_list('pk', flat=True))

    def test_remove_non_existent_document(self):
        response = self.post_page(ProjectFactory(), {
            'form-submitted-remove_document_form': '',
            'id': 1,
        })
        self.assertEqual(response.status_code, 200)


class TestSendForApprovalView(BaseViewTestCase):
    base_view_name = 'detail'
    url_name = 'funds:projects:{}'
    user_factory = StaffFactory

    def get_kwargs(self, instance):
        return {'pk': instance.id}

    def test_send_for_approval_fails_when_project_is_locked(self):
        project = ProjectFactory(is_locked=True)

        # The view doesn't have any custom changes when form validation fails
        # so check that directly.
        form = SetPendingForm(instance=project)
        self.assertFalse(form.is_valid())

    def test_send_for_approval_fails_when_project_is_not_in_committed_state(self):
        project = ProjectFactory(status='in_progress')

        # The view doesn't have any custom changes when form validation fails
        # so check that directly.
        form = SetPendingForm(instance=project)
        self.assertFalse(form.is_valid())

    def test_send_for_approval_happy_path(self):
        project = ProjectFactory(is_locked=False, status='committed')

        response = self.post_page(project, {'form-submitted-request_approval_form': ''})
        self.assertEqual(response.status_code, 200)

        project.refresh_from_db()

        self.assertTrue(project.is_locked)
        self.assertEqual(project.status, 'committed')


class TestUploadDocumentView(BaseViewTestCase):
    base_view_name = 'detail'
    url_name = 'funds:projects:{}'
    user_factory = StaffFactory

    def get_kwargs(self, instance):
        return {'pk': instance.id}

    def test_upload_document(self):
        category = DocumentCategoryFactory()
        project = ProjectFactory()

        test_doc = BytesIO(b'somebinarydata')
        test_doc.name = 'document.pdf'

        response = self.post_page(project, {
            'form-submitted-document_form': '',
            'title': 'test document',
            'category': category.id,
            'document': test_doc,
        })
        self.assertEqual(response.status_code, 200)

        project.refresh_from_db()

        self.assertEqual(project.packet_files.count(), 1)


class BaseProjectEditTestCase(BaseViewTestCase):
    url_name = 'funds:projects:{}'
    base_view_name = 'edit'

    def get_kwargs(self, instance):
        return {'pk': instance.id}


class TestUserProjectEditView(BaseProjectEditTestCase):
    user_factory = UserFactory

    def test_does_not_have_access(self):
        project = ProjectFactory()
        response = self.get_page(project)

        self.assertEqual(response.status_code, 403)

    def test_owner_has_access(self):
        project = ProjectFactory(user=self.user)
        response = self.get_page(project)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])

    def test_no_lead_redirects(self):
        project = ProjectFactory(user=self.user, lead=None)
        response = self.get_page(project)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.url(project, 'detail'))

    def test_locked_redirects(self):
        project = ProjectFactory(user=self.user, is_locked=True)
        response = self.get_page(project)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.url(project, 'detail'))


class TestStaffProjectEditView(BaseProjectEditTestCase):
    user_factory = StaffFactory

    def test_staff_user_has_access(self):
        project = ProjectFactory()
        response = self.get_page(project)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])

    def test_no_lead_redirects(self):
        project = ProjectFactory(user=self.user, lead=None)
        response = self.get_page(project)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.url(project, 'detail'))

    def test_locked_redirects(self):
        project = ProjectFactory(user=self.user, is_locked=True)
        response = self.get_page(project)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.url(project, 'detail'))


class TestApproverProjectEditView(BaseProjectEditTestCase):
    user_factory = ApproverFactory

    def test_approver_has_access_locked(self):
        project = ProjectFactory(is_locked=True)
        response = self.get_page(project)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])


class TestSuperProjectEditView(BaseProjectEditTestCase):
    user_factory = StaffFactory

    def test_has_access(self):
        project = ProjectFactory()
        response = self.get_page(project)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])


class TestReviewerProjectEditView(BaseProjectEditTestCase):
    user_factory = ReviewerFactory

    def test_does_not_have_access(self):
        project = ProjectFactory()
        response = self.get_page(project)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.redirect_chain, [])