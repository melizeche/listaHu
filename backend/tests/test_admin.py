"""Smoke tests for the moderation admin."""

from django.contrib.admin.sites import site
from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User

from backend.admin import DenunciaAdmin
from backend.models import Denuncia, Estadistica, Tipo
from backend.tests.helpers import get_tipo, make_denuncia


class AdminRegistrationTests(TestCase):
    def test_every_model_is_registered(self):
        for model in (Denuncia, Tipo, Estadistica):
            self.assertIn(model, site._registry)

    def test_moderators_can_filter_the_report_list(self):
        self.assertEqual(DenunciaAdmin.list_filter, ("tipo", "check", "activo"))

    def test_moderators_can_search_reports(self):
        self.assertIn("numero", DenunciaAdmin.search_fields)


class AdminViewTests(TestCase):
    def setUp(self):
        User.objects.create_superuser("admin", "admin@listahu.org", "secreto")
        self.client.login(username="admin", password="secreto")
        self.denuncia = make_denuncia(numero="0981123456", tipo=get_tipo("Estafa"))

    def test_report_changelist_renders(self):
        response = self.client.get(reverse("admin:backend_denuncia_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "595981123456")

    def test_report_changelist_is_searchable(self):
        response = self.client.get(
            reverse("admin:backend_denuncia_changelist"), {"q": "595981123456"}
        )
        self.assertContains(response, "595981123456")

    def test_report_detail_renders(self):
        response = self.client.get(
            reverse("admin:backend_denuncia_change", args=[self.denuncia.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_tipo_changelist_renders(self):
        response = self.client.get(reverse("admin:backend_tipo_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Estafa")

    def test_estadistica_changelist_renders(self):
        response = self.client.get(reverse("admin:backend_estadistica_changelist"))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_users_are_redirected_to_the_login_page(self):
        self.client.logout()
        response = self.client.get(reverse("admin:backend_denuncia_changelist"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_moderator_can_deactivate_a_report(self):
        Denuncia.objects.filter(pk=self.denuncia.pk).update(activo=False)
        response = self.client.get(reverse("admin:backend_denuncia_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Denuncia.objects.get(pk=self.denuncia.pk).activo)
