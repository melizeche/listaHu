"""Tests for the public HTML views."""

import unittest

from django.test import TestCase
from django.urls import reverse

from backend.models import Denuncia, Estadistica
from backend.tests.helpers import (
    get_tipo,
    make_denuncia,
    make_image_file,
    quiet_stdout,
    supports_distinct_on_fields,
)

needs_postgres = unittest.skipUnless(
    supports_distinct_on_fields(),
    "requires a backend with DISTINCT ON support (PostgreSQL)",
)


def report_payload(numero="0981123456", desc="Me escribieron a las 3am"):
    return {
        "tipo": get_tipo().pk,
        "numero": numero,
        "desc": desc,
        "screenshot": make_image_file(),
    }


class HomeViewTests(TestCase):
    def test_get_renders_the_report_form(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertIn("form", response.context)

    def test_counter_is_empty_before_the_first_report(self):
        self.assertEqual(self.client.get(reverse("home")).context["denuncias"], "")

    def test_counter_is_shown_once_reports_exist(self):
        make_denuncia()
        self.assertEqual(self.client.get(reverse("home")).context["denuncias"], 1)

    def test_valid_post_creates_the_report(self):
        self.client.post(reverse("home"), report_payload())
        self.assertEqual(Denuncia.objects.count(), 1)
        self.assertEqual(Denuncia.objects.get().numero, "595981123456")

    def test_valid_post_redirects_to_the_search_page(self):
        response = self.client.post(
            reverse("home"), report_payload(numero="0981123456")
        )
        # The redirect uses the raw input, and relies on APPEND_SLASH to reach
        # the canonical ``/buscar/<numero>/`` URL.
        self.assertRedirects(
            response, "/buscar/0981123456", status_code=302, target_status_code=301
        )

    def test_valid_post_leaves_a_success_message(self):
        with quiet_stdout():  # following the redirect lands on ``buscar``
            response = self.client.post(reverse("home"), report_payload(), follow=True)
        self.assertIn(
            "Se agregó correctamente!", [str(m) for m in response.context["messages"]]
        )

    def test_invalid_post_is_reported_back_to_the_user(self):
        response = self.client.post(reverse("home"), report_payload(numero="123"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["fail"], "fail")
        self.assertEqual(Denuncia.objects.count(), 0)

    def test_post_without_screenshot_is_rejected(self):
        payload = report_payload()
        del payload["screenshot"]
        response = self.client.post(reverse("home"), payload)
        self.assertEqual(response.context["fail"], "fail")
        self.assertEqual(Denuncia.objects.count(), 0)


class BuscarViewTests(TestCase):
    def test_search_page_without_a_number_renders_empty(self):
        response = self.client.get(reverse("buscar"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "buscar.html")
        self.assertEqual(response.context["msg"], "")

    def test_known_number_is_found(self):
        make_denuncia(numero="0981123456")
        with quiet_stdout():
            response = self.client.get(reverse("buscar", args=["595981123456"]))
        self.assertEqual(response.context["msg"], "595981123456")
        self.assertEqual(len(response.context["withthumbs"]), 1)

    def test_search_normalises_the_query(self):
        make_denuncia(numero="0981123456")
        with quiet_stdout():
            response = self.client.get(reverse("buscar", args=["0981123456"]))
        self.assertEqual(response.context["msg"], "595981123456")

    def test_unknown_number_shows_a_friendly_message(self):
        with quiet_stdout():
            response = self.client.get(reverse("buscar", args=["0981999999"]))
        self.assertEqual(
            response.context["msg"],
            "No se encontró 0981999999 en la base de datos",
        )

    def test_inactive_reports_are_hidden(self):
        denuncia = make_denuncia(numero="0981123456")
        Denuncia.objects.filter(pk=denuncia.pk).update(activo=False)
        with quiet_stdout():
            response = self.client.get(reverse("buscar", args=["0981123456"]))
        self.assertIn("No se encontró", response.context["msg"])

    def test_every_match_is_paired_with_its_thumbnail_path(self):
        make_denuncia(numero="0981123456")
        make_denuncia(numero="0981123456")
        with quiet_stdout():
            response = self.client.get(reverse("buscar", args=["0981123456"]))
        self.assertEqual(len(response.context["withthumbs"]), 2)
        for denuncia, thumb in response.context["withthumbs"]:
            self.assertTrue(thumb.endswith("_th.png"))
            self.assertTrue(thumb.startswith("denuncias/"))


class NavegarViewTests(TestCase):
    def test_page_renders(self):
        response = self.client.get(reverse("navegar"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "navegar.html")


class DenunciaViewTests(TestCase):
    def test_get_renders_the_form(self):
        response = self.client.get(reverse("denuncia"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "denuncia.html")
        self.assertIn("form", response.context)

    def test_valid_post_creates_the_report_and_redirects(self):
        response = self.client.post(reverse("denuncia"), report_payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Denuncia.objects.count(), 1)

    def test_invalid_post_redisplays_the_form(self):
        response = self.client.post(reverse("denuncia"), report_payload(numero="123"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(Denuncia.objects.count(), 0)


class TopDenunciasViewTests(TestCase):
    def test_page_renders(self):
        response = self.client.get(reverse("top"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "top.html")

    def test_numbers_are_ranked_by_number_of_reports(self):
        for _ in range(3):
            make_denuncia(numero="0981111111")
        make_denuncia(numero="0982222222")
        numeros = list(self.client.get(reverse("top")).context["numeros"])
        self.assertEqual(numeros[0], {"numero": "595981111111", "count": 3})
        self.assertEqual(numeros[1], {"numero": "595982222222", "count": 1})

    def test_inactive_reports_are_excluded(self):
        denuncia = make_denuncia(numero="0981111111")
        Denuncia.objects.filter(pk=denuncia.pk).update(activo=False)
        self.assertEqual(list(self.client.get(reverse("top")).context["numeros"]), [])

    def test_ranking_is_capped_at_fifty_numbers(self):
        for i in range(55):
            make_denuncia(numero="09811%05d" % i)
        self.assertEqual(len(self.client.get(reverse("top")).context["numeros"]), 50)


class DownloadViewTests(TestCase):
    def setUp(self):
        self.denuncia = make_denuncia(numero="0981123456", desc="spam de prueba")

    def test_landing_page_renders_without_a_format(self):
        response = self.client.get(reverse("descargar"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "descargar.html")

    def test_unknown_format_falls_back_to_the_landing_page(self):
        response = self.client.get(reverse("archivos", args=["xlsx"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "descargar.html")

    def test_csv_export_content_type_and_filename(self):
        response = self.client.get(reverse("archivos", args=["csv"]))
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertRegex(
            response["Content-Disposition"],
            r'attachment; filename="LISTA_HU_\d{4}-\d{2}-\d{2}\.csv"',
        )

    def test_csv_export_contains_the_reports(self):
        body = self.client.get(reverse("archivos", args=["csv"])).content.decode()
        self.assertIn("595981123456", body)
        self.assertIn("spam de prueba", body)

    def test_csv_export_skips_inactive_reports(self):
        Denuncia.objects.filter(pk=self.denuncia.pk).update(activo=False)
        body = self.client.get(reverse("archivos", args=["csv"])).content.decode()
        self.assertNotIn("595981123456", body)

    def test_repeated_numbers_vcard(self):
        make_denuncia(numero="0981123456")
        with quiet_stdout():
            response = self.client.get(reverse("archivos", args=["vcard/repetidos"]))
        self.assertEqual(response["Content-Type"], "text/vcard")
        self.assertIn("+595981123456", response.content.decode())

    def test_repeated_numbers_vcard_excludes_single_reports(self):
        make_denuncia(numero="0982222222")
        with quiet_stdout():
            response = self.client.get(reverse("archivos", args=["vcard/repetidos"]))
        self.assertNotIn("+595982222222", response.content.decode())

    def test_repeated_numbers_vcard_filename(self):
        with quiet_stdout():
            response = self.client.get(reverse("archivos", args=["vcard/repetidos"]))
        self.assertRegex(
            response["Content-Disposition"],
            r'attachment; filename="LISTA_HU_REP_\d{4}-\d{2}-\d{2}\.VCF"',
        )

    @needs_postgres
    def test_full_vcard_export(self):
        with quiet_stdout():
            response = self.client.get(reverse("archivos", args=["vcard"]))
        self.assertEqual(response["Content-Type"], "text/vcard")
        self.assertIn("+595981123456", response.content.decode())

    @needs_postgres
    def test_nospam_vcard_export_excludes_spam(self):
        make_denuncia(numero="0982222222", tipo=get_tipo("Estafa"))
        with quiet_stdout():
            response = self.client.get(reverse("archivos", args=["vcard/nospam"]))
        body = response.content.decode()
        self.assertIn("+595982222222", body)
        self.assertNotIn("+595981123456", body)


class StaticPageTests(TestCase):
    def test_contact_page(self):
        self.assertEqual(self.client.get("/contacto/").status_code, 200)

    def test_legal_page(self):
        self.assertEqual(self.client.get("/legal/").status_code, 200)

    def test_api_documentation_page(self):
        self.assertEqual(self.client.get("/api/").status_code, 200)


class StatsIntegrationTests(TestCase):
    def test_home_counter_tracks_reports_filed_through_the_form(self):
        self.client.post(reverse("home"), report_payload(numero="0981123456"))
        self.client.post(reverse("home"), report_payload(numero="0982222222"))
        self.assertEqual(Estadistica.objects.get(nombre="denuncias").valor, 2)
        self.assertEqual(self.client.get(reverse("home")).context["denuncias"], 2)
