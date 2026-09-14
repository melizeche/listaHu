"""Tests for :mod:`backend.models`: normalisation, uploads and signals."""

import os

from django.conf import settings
from django.test import SimpleTestCase, TestCase

from backend.models import Denuncia, Estadistica, Tipo, rename
from backend.tests.helpers import get_tipo, make_denuncia, make_image_file


class RenameTests(SimpleTestCase):
    """``rename`` builds the upload path for a screenshot."""

    def test_path_starts_with_the_denuncias_folder(self):
        path = rename(Denuncia(numero="595981123456"), "captura.png")
        self.assertTrue(path.startswith(os.path.join("denuncias", "")))

    def test_number_and_timestamp_are_prefixed_to_the_filename(self):
        path = rename(Denuncia(numero="595981123456"), "captura.png")
        self.assertRegex(path, r"^denuncias/595981123456_\d{12}_captura\.png$")

    def test_missing_number_falls_back_to_a_timestamp_only_name(self):
        path = rename(Denuncia(numero=""), "captura.png")
        self.assertRegex(path, r"^denuncias/\d{12}-captura\.png$")

    def test_spaces_in_the_filename_are_replaced(self):
        path = rename(Denuncia(numero="595981123456"), "mi captura.png")
        self.assertTrue(path.endswith("_mi_captura.png"))
        self.assertNotIn(" ", path)


class DenunciaValidateNumberTests(SimpleTestCase):
    """The model carries its own copy of the normalisation logic."""

    def setUp(self):
        self.denuncia = Denuncia()

    def test_local_prefix_is_expanded(self):
        self.assertEqual(self.denuncia.validateNumber("0981123456"), "595981123456")

    def test_leading_plus_is_dropped(self):
        self.assertEqual(self.denuncia.validateNumber("+595981123456"), "595981123456")

    def test_separators_and_direction_marks_are_stripped(self):
        self.assertEqual(
            self.denuncia.validateNumber("‭(0981) 123-456‬"), "595981123456"
        )

    def test_short_numbers_are_returned_as_is(self):
        # Both branches of the length check return the same value, so a number
        # that is not 12 digits long is still handed back normalised.
        self.assertEqual(self.denuncia.validateNumber("12345"), "12345")


class DenunciaSaveTests(TestCase):
    def test_number_is_normalised_on_save(self):
        denuncia = make_denuncia(numero="0981123456")
        self.assertEqual(denuncia.numero, "595981123456")
        denuncia.refresh_from_db()
        self.assertEqual(denuncia.numero, "595981123456")

    def test_numeric_report_stays_active(self):
        self.assertTrue(make_denuncia(numero="0981123456").activo)

    def test_report_with_non_digits_is_deactivated(self):
        # Garbage entries are kept but hidden from every public listing.
        self.assertFalse(make_denuncia(numero="no-es-un-numero").activo)

    def test_normalisation_is_idempotent_across_saves(self):
        denuncia = make_denuncia(numero="0981123456")
        denuncia.save()
        self.assertEqual(denuncia.numero, "595981123456")

    def test_str_shows_the_number_and_the_type(self):
        denuncia = make_denuncia(numero="0981123456", tipo=get_tipo("Estafa"))
        self.assertEqual(str(denuncia), "595981123456 - Estafa")

    def test_defaults(self):
        denuncia = make_denuncia()
        self.assertEqual(denuncia.votsi, 0)
        self.assertEqual(denuncia.votno, 0)
        self.assertFalse(denuncia.check)
        self.assertIsNotNone(denuncia.added)

    def test_screenshot_is_stored_under_the_denuncias_folder(self):
        denuncia = make_denuncia(numero="0981123456")
        self.assertTrue(str(denuncia.screenshot).startswith("denuncias/"))
        self.assertIn("595981123456", str(denuncia.screenshot))


class TipoTests(TestCase):
    def test_migration_seeds_the_three_report_types(self):
        self.assertEqual(
            sorted(Tipo.objects.values_list("titulo", flat=True)),
            ["Estafa", "Extorsión", "SPAM"],
        )

    def test_slug_is_derived_from_the_title(self):
        tipo = Tipo.objects.create(titulo="Llamada Perdida")
        self.assertEqual(tipo.slug, "llamada-perdida")

    def test_slug_is_unique(self):
        first = Tipo.objects.create(titulo="Duplicado")
        second = Tipo.objects.create(titulo="Duplicado")
        self.assertNotEqual(first.slug, second.slug)

    def test_str_is_the_title(self):
        self.assertEqual(str(get_tipo("SPAM")), "SPAM")


class EstadisticaTests(TestCase):
    def test_str_is_the_name(self):
        self.assertEqual(
            str(Estadistica.objects.create(nombre="denuncias")), "denuncias"
        )

    def test_value_defaults_to_zero(self):
        self.assertEqual(Estadistica.objects.create(nombre="otra").valor, 0)


class UpdateStatsSignalTests(TestCase):
    """The ``denuncias`` counter is maintained by a ``post_save`` signal."""

    def test_counter_row_is_created_with_the_first_report(self):
        self.assertFalse(Estadistica.objects.filter(nombre="denuncias").exists())
        make_denuncia()
        self.assertEqual(Estadistica.objects.get(nombre="denuncias").valor, 1)

    def test_counter_is_updated_on_every_new_report(self):
        make_denuncia(numero="0981123456")
        make_denuncia(numero="0981654321")
        self.assertEqual(Estadistica.objects.get(nombre="denuncias").valor, 2)

    def test_counter_is_not_touched_when_a_report_is_edited(self):
        denuncia = make_denuncia()
        denuncia.desc = "editado"
        denuncia.save()
        self.assertEqual(Estadistica.objects.get(nombre="denuncias").valor, 1)

    def test_only_one_counter_row_is_kept(self):
        make_denuncia(numero="0981123456")
        make_denuncia(numero="0981654321")
        self.assertEqual(Estadistica.objects.filter(nombre="denuncias").count(), 1)

    def test_inactive_reports_are_counted_too(self):
        # ``update_stats`` counts every row, including the ones ``save``
        # deactivated for not being a phone number.
        make_denuncia(numero="no-es-un-numero")
        self.assertEqual(Estadistica.objects.get(nombre="denuncias").valor, 1)


class ThumbnailSignalTests(TestCase):
    def test_thumbnail_is_generated_for_a_new_report(self):
        denuncia = make_denuncia()
        base, ext = os.path.splitext(settings.MEDIA_ROOT + str(denuncia.screenshot))
        self.assertTrue(os.path.exists("%s_th%s" % (base, ext)))

    def test_creating_a_report_never_fails_because_of_the_thumbnail(self):
        # The signal swallows errors on purpose: a broken screenshot must not
        # stop a report from being filed.
        denuncia = Denuncia.objects.create(
            tipo=get_tipo(),
            numero="0981123456",
            screenshot=make_image_file(name="captura.png"),
        )
        denuncia.screenshot.delete(save=False)
        denuncia.save()
        self.assertTrue(Denuncia.objects.filter(pk=denuncia.pk).exists())
