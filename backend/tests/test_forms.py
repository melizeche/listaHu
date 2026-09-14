"""Tests for the public report form."""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from backend.forms import DenunciaForm
from backend.tests.helpers import get_tipo, make_image_file


class DenunciaFormTests(TestCase):
    def build(self, numero="0981123456", with_screenshot=True, **extra):
        data = {"tipo": get_tipo().pk, "numero": numero, "desc": "Me escribieron"}
        data.update(extra)
        files = {"screenshot": make_image_file()} if with_screenshot else {}
        return DenunciaForm(data=data, files=files)

    def test_valid_report_is_accepted(self):
        form = self.build()
        self.assertTrue(form.is_valid(), form.errors)

    def test_saving_normalises_the_number(self):
        form = self.build(numero="0981123456")
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().numero, "595981123456")

    def test_cleaned_number_keeps_the_raw_user_input(self):
        # ``home`` redirects using this value, so the search page has to accept
        # the un-normalised form as well.
        form = self.build(numero="0981123456")
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["numero"], "0981123456")

    def test_short_numbers_are_rejected_with_a_custom_message(self):
        form = self.build(numero="098112")
        self.assertFalse(form.is_valid())
        self.assertIn("No se aceptan números cortos", form.errors["numero"][0])

    def test_long_numbers_are_rejected(self):
        form = self.build(numero="5959811234567890")
        self.assertFalse(form.is_valid())
        self.assertIn("numero", form.errors)

    def test_screenshot_is_mandatory(self):
        form = self.build(with_screenshot=False)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["screenshot"], ["Es obligatorio agregar la captura de pantalla"]
        )

    def test_a_non_image_upload_is_rejected(self):
        upload = SimpleUploadedFile(
            "nota.txt", b"esto no es una imagen", content_type="text/plain"
        )
        form = DenunciaForm(
            data={"tipo": get_tipo().pk, "numero": "0981123456", "desc": ""},
            files={"screenshot": upload},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("screenshot", form.errors)

    def test_tipo_is_mandatory(self):
        form = self.build(tipo="")
        self.assertFalse(form.is_valid())
        self.assertIn("tipo", form.errors)

    def test_description_is_optional(self):
        form = self.build(desc="")
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_only_exposes_the_public_fields(self):
        # ``activo``, ``check`` and the vote counters are moderation-only.
        self.assertEqual(
            list(DenunciaForm().fields), ["tipo", "numero", "screenshot", "desc"]
        )
