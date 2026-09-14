"""Tests for the public REST API (``/api/v1/``)."""

import unittest

from django.contrib.auth.models import User
from django.test import TestCase

from backend.models import Denuncia
from backend.tests.helpers import (
    get_tipo,
    make_denuncia,
    make_image_file,
    supports_distinct_on_fields,
)

needs_postgres = unittest.skipUnless(
    supports_distinct_on_fields(),
    "requires a backend with DISTINCT ON support (PostgreSQL)",
)


class ListaEndpointTests(TestCase):
    url = "/api/v1/lista/"

    def setUp(self):
        self.spam = make_denuncia(numero="0981111111", tipo=get_tipo("SPAM"))
        self.estafa = make_denuncia(numero="0982222222", tipo=get_tipo("Estafa"))

    def test_readable_without_authentication(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_returns_a_plain_list_not_a_paginated_envelope(self):
        # ``ListaViewSet`` overrides ``list()``, which bypasses pagination.
        self.assertIsInstance(self.client.get(self.url).json(), list)

    def test_every_active_report_is_returned(self):
        self.assertEqual(len(self.client.get(self.url).json()), 2)

    def test_inactive_reports_are_hidden(self):
        Denuncia.objects.filter(pk=self.spam.pk).update(activo=False)
        numbers = [row["numero"] for row in self.client.get(self.url).json()]
        self.assertNotIn("595981111111", numbers)

    def test_tipo_is_rendered_as_a_title(self):
        rows = {row["numero"]: row["tipo"] for row in self.client.get(self.url).json()}
        self.assertEqual(rows["595982222222"], "Estafa")

    def test_results_can_be_filtered_by_tipo(self):
        response = self.client.get(self.url, {"tipo": get_tipo("SPAM").slug})
        self.assertEqual([row["numero"] for row in response.json()], ["595981111111"])

    def test_results_can_be_filtered_by_numero(self):
        response = self.client.get(self.url, {"numero": "982222"})
        self.assertEqual([row["numero"] for row in response.json()], ["595982222222"])


class DenunciasEndpointTests(TestCase):
    url = "/api/v1/denuncias/"

    def setUp(self):
        self.spam = make_denuncia(numero="0981111111", tipo=get_tipo("SPAM"))
        self.estafa = make_denuncia(numero="0982222222", tipo=get_tipo("Estafa"))

    def test_readable_without_authentication(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_response_is_paginated(self):
        payload = self.client.get(self.url).json()
        self.assertEqual(payload["count"], 2)
        self.assertIn("results", payload)

    def test_results_are_newest_first(self):
        numbers = [row["numero"] for row in self.client.get(self.url).json()["results"]]
        self.assertEqual(numbers, ["595982222222", "595981111111"])

    def test_inactive_reports_are_hidden(self):
        Denuncia.objects.filter(pk=self.spam.pk).update(activo=False)
        self.assertEqual(self.client.get(self.url).json()["count"], 1)

    def test_detail_route_serves_a_single_report(self):
        payload = self.client.get("%s%d/" % (self.url, self.spam.pk)).json()
        self.assertEqual(payload["numero"], "595981111111")

    def test_filter_by_tipo(self):
        payload = self.client.get(self.url, {"tipo": get_tipo("Estafa").slug}).json()
        self.assertEqual(payload["count"], 1)

    def test_filter_by_numero_substring(self):
        payload = self.client.get(self.url, {"numero": "981111"}).json()
        self.assertEqual(payload["count"], 1)

    def test_filter_by_id_range(self):
        payload = self.client.get(self.url, {"id_from": self.estafa.pk}).json()
        self.assertEqual(payload["count"], 1)

    def test_anonymous_users_cannot_post(self):
        response = self.client.post(self.url, {"numero": "0981333333"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Denuncia.objects.count(), 2)

    def test_anonymous_users_cannot_delete(self):
        response = self.client.delete("%s%d/" % (self.url, self.spam.pk))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Denuncia.objects.filter(pk=self.spam.pk).exists())

    @unittest.expectedFailure
    def test_authenticated_users_can_post(self):
        """KNOWN BUG: creating a report through the API is impossible.

        ``DenunciaSerializer.tipo`` is a ``SlugRelatedField(read_only=True)``,
        so ``tipo`` is stripped from the validated data and the insert dies on
        the ``NOT NULL`` foreign key with a 500 instead of creating the row.
        Making ``tipo`` writable (for instance a ``SlugRelatedField`` with
        ``queryset=Tipo.objects.all()``) is what this test is waiting for.
        """
        User.objects.create_user("moderador", password="secreto")
        self.client.login(username="moderador", password="secreto")
        response = self.client.post(
            self.url,
            {
                "tipo": "SPAM",
                "numero": "0981333333",
                "desc": "nuevo",
                "screenshot": make_image_file(),
            },
        )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(Denuncia.objects.filter(numero="595981333333").count(), 1)

    def test_json_output_is_indented(self):
        # ``get_renderer_context`` sets an indent so the API stays readable.
        self.assertIn(
            b"\n    ", self.client.get(self.url, HTTP_ACCEPT="application/json").content
        )


class NumerosEndpointTests(TestCase):
    url = "/api/v1/numeros/"

    @needs_postgres
    def test_readable_without_authentication(self):
        make_denuncia(numero="0981111111")
        self.assertEqual(self.client.get(self.url).status_code, 200)

    @needs_postgres
    def test_duplicated_numbers_are_collapsed(self):
        make_denuncia(numero="0981111111")
        make_denuncia(numero="0981111111")
        make_denuncia(numero="0982222222")
        numbers = [row["numero"] for row in self.client.get(self.url).json()]
        self.assertEqual(sorted(numbers), ["595981111111", "595982222222"])

    @needs_postgres
    def test_results_can_be_filtered(self):
        make_denuncia(numero="0981111111")
        make_denuncia(numero="0982222222")
        response = self.client.get(self.url, {"numero": "981111"})
        self.assertEqual([row["numero"] for row in response.json()], ["595981111111"])


class CorsTests(TestCase):
    def test_denuncias_endpoint_is_open_to_other_origins(self):
        response = self.client.get(
            "/api/v1/denuncias/", HTTP_ORIGIN="https://ejemplo.com"
        )
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")

    def test_other_endpoints_are_not_cors_enabled(self):
        # ``CORS_URLS_REGEX`` limits the headers to ``/api/v1/denuncias``.
        response = self.client.get("/api/v1/lista/", HTTP_ORIGIN="https://ejemplo.com")
        self.assertNotIn("Access-Control-Allow-Origin", response)


class ApiRootTests(TestCase):
    """The router index itself is admin-only; the endpoints under it are not."""

    url = "/api/v1/"

    def login_as_admin(self):
        User.objects.create_superuser("admin", "admin@listahu.org", "secreto")
        self.client.login(username="admin", password="secreto")

    def test_anonymous_users_cannot_read_the_index(self):
        # The router view falls back to the project-wide ``IsAdminUser``.
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_admin_sees_every_endpoint(self):
        self.login_as_admin()
        payload = self.client.get(self.url, HTTP_ACCEPT="application/json").json()
        self.assertEqual(set(payload), {"lista", "denuncias", "numeros"})

    def test_each_endpoint_is_advertised_with_its_own_url(self):
        """The three endpoints each get their own route name.

        All three viewsets expose ``queryset = Denuncia.objects...``, so the
        router used to derive the same basename (``denuncia``) for each
        registration and ``reverse()`` resolved every one of them to the last
        one declared -- the index linked to ``/api/v1/numeros/`` three times.
        ``conf.urls`` now passes an explicit ``basename`` per registration.
        """
        self.login_as_admin()
        payload = self.client.get(self.url, HTTP_ACCEPT="application/json").json()
        self.assertEqual(len(set(payload.values())), 3)

    def test_the_endpoints_themselves_are_reachable(self):
        # The colliding route *names* do not affect the actual URL paths.
        for path in ("/api/v1/lista/", "/api/v1/denuncias/"):
            self.assertEqual(self.client.get(path).status_code, 200, path)
