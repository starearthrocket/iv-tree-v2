from django.contrib.auth.models import User
from django.test import TestCase

from .forms import ProgressUpdateForm, RegisterForm, TreeReportForm
from .models import ProgressUpdate, TreeReport


class TreeReportModelTest(TestCase):
    """Tests for the TreeReport model."""

    def setUp(self):
        """Create a user and tree report for testing."""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
        )

        self.report = TreeReport.objects.create(
            owner=self.user,
            location="Test Woodland",
            description="Tree affected by invasive ivy.",
            status="reported",
        )

    def test_tree_report_created(self):
        """Test that a tree report is created correctly."""
        self.assertEqual(self.report.location, "Test Woodland")
        self.assertEqual(
            self.report.description,
            "Tree affected by invasive ivy.",
        )
        self.assertEqual(self.report.status, "reported")
        self.assertEqual(self.report.owner, self.user)

    def test_tree_report_string_method(self):
        """Test the TreeReport string representation."""
        self.assertEqual(str(self.report), "Test Woodland")


class ProgressUpdateModelTest(TestCase):
    """Tests for ProgressUpdate relationships."""

    def setUp(self):
        """Create a user, report and progress updates for testing."""
        self.user = User.objects.create_user(
            username="updateuser",
            password="testpassword123",
        )

        self.report = TreeReport.objects.create(
            owner=self.user,
            location="Community Park",
            description="Ivy growth reported.",
        )

        self.update_one = ProgressUpdate.objects.create(
            owner=self.user,
            tree_report=self.report,
            notes="Initial monitoring update.",
            status="monitoring",
        )

        self.update_two = ProgressUpdate.objects.create(
            owner=self.user,
            tree_report=self.report,
            notes="Further progress recorded.",
            status="protected",
        )

    def test_report_has_multiple_progress_updates(self):
        """Test one report can have multiple related updates."""
        self.assertEqual(self.report.progress_updates.count(), 2)

    def test_progress_update_string_method(self):
        """Test the ProgressUpdate string representation."""
        self.assertEqual(
            str(self.update_one),
            "Update for Community Park",
        )

    def test_deleting_report_deletes_progress_updates(self):
        """Test related updates are deleted with their report."""
        self.report.delete()

        self.assertEqual(
            ProgressUpdate.objects.count(),
            0,
        )


class FormTest(TestCase):
    """Tests for report, progress update and registration forms."""

    def test_tree_report_form_valid(self):
        """Test valid tree report data is accepted."""
        form = TreeReportForm(
            data={
                "location": "Riverside Park",
                "description": "Tree with significant ivy growth.",
            }
        )

        self.assertTrue(form.is_valid())

    def test_progress_update_form_valid(self):
        """Test valid progress update data is accepted."""
        form = ProgressUpdateForm(
            data={
                "notes": "Ivy has been reduced.",
                "status": "protected",
            }
        )

        self.assertTrue(form.is_valid())

    def test_register_form_valid(self):
        """Test valid registration data is accepted."""
        form = RegisterForm(
            data={
                "username": "newtestuser",
                "password1": "SecureTestPassword123!",
                "password2": "SecureTestPassword123!",
            }
        )

        self.assertTrue(form.is_valid())


class PublicViewTest(TestCase):
    """Tests for public pages and login protection."""

    def setUp(self):
        """Create a report for public view tests."""
        self.report = TreeReport.objects.create(
            location="Public Test Tree",
            description="Tree used for public page testing.",
        )

    def test_home_page_loads(self):
        """Test the homepage loads successfully."""
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)

    def test_about_page_loads(self):
        """Test the About page loads successfully."""
        response = self.client.get("/about/")

        self.assertEqual(response.status_code, 200)

    def test_report_list_loads(self):
        """Test the tree report list loads successfully."""
        response = self.client.get("/reports/")

        self.assertEqual(response.status_code, 200)

    def test_invalid_report_returns_404(self):
        """Test an invalid tree report ID returns a 404."""
        response = self.client.get("/reports/999999/")

        self.assertEqual(response.status_code, 404)

    def test_logged_out_user_cannot_access_report_form(self):
        """Test report creation requires authentication."""
        response = self.client.get("/report/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)


class TreeReportPermissionTest(TestCase):
    """Tests for tree report creation and ownership permissions."""

    def setUp(self):
        """Create two users and an owned tree report."""
        self.owner = User.objects.create_user(
            username="reportowner",
            password="testpassword123",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="testpassword123",
        )

        self.report = TreeReport.objects.create(
            owner=self.owner,
            location="Owned Tree",
            description="Report belonging to the owner.",
        )

    def test_logged_in_user_can_create_report(self):
        """Test an authenticated user can create a tree report."""
        self.client.login(
            username="reportowner",
            password="testpassword123",
        )

        response = self.client.post(
            "/report/",
            {
                "location": "New Test Tree",
                "description": "New report created during testing.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            TreeReport.objects.filter(
                location="New Test Tree",
            ).exists()
        )

    def test_created_report_belongs_to_logged_in_user(self):
        """Test a new report is assigned to its creator."""
        self.client.login(
            username="otheruser",
            password="testpassword123",
        )

        self.client.post(
            "/report/",
            {
                "location": "Ownership Test Tree",
                "description": "Testing automatic ownership.",
            },
        )

        report = TreeReport.objects.get(
            location="Ownership Test Tree",
        )

        self.assertEqual(report.owner, self.other_user)

    def test_owner_can_edit_report(self):
        """Test the report owner can edit their report."""
        self.client.login(
            username="reportowner",
            password="testpassword123",
        )

        response = self.client.post(
            f"/reports/{self.report.pk}/edit/",
            {
                "location": "Edited Tree",
                "description": "Report successfully edited.",
            },
        )

        self.report.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.report.location, "Edited Tree")

    def test_other_user_cannot_edit_report(self):
        """Test another user cannot edit someone else's report."""
        self.client.login(
            username="otheruser",
            password="testpassword123",
        )

        self.client.post(
            f"/reports/{self.report.pk}/edit/",
            {
                "location": "Unauthorised Edit",
                "description": "This should not be saved.",
            },
        )

        self.report.refresh_from_db()

        self.assertEqual(self.report.location, "Owned Tree")

    def test_owner_can_delete_report(self):
        """Test the report owner can delete their report."""
        self.client.login(
            username="reportowner",
            password="testpassword123",
        )

        response = self.client.post(
            f"/reports/{self.report.pk}/delete/",
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            TreeReport.objects.filter(
                pk=self.report.pk,
            ).exists()
        )

    def test_other_user_cannot_delete_report(self):
        """Test another user cannot delete someone else's report."""
        self.client.login(
            username="otheruser",
            password="testpassword123",
        )

        response = self.client.post(
            f"/reports/{self.report.pk}/delete/",
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            TreeReport.objects.filter(
                pk=self.report.pk,
            ).exists()
        )