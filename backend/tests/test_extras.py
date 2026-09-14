"""Tests for the pure helper functions in :mod:`backend.extras`."""

import os
import re
import tempfile

from PIL import Image
from django.test import SimpleTestCase, TestCase

from backend.extras import (
    PrettyJsonRenderer,
    create_thumbnail,
    create_vcard,
    getCSV,
    split_list,
    thumbnail_all,
    validateNumber,
    vcard,
)
from backend.models import Denuncia
from backend.tests.helpers import make_denuncia, quiet_stdout


class ValidateNumberTests(SimpleTestCase):
    """``validateNumber`` normalises user input to the 595XXXXXXXXX form."""

    def test_local_prefix_is_expanded_to_country_code(self):
        self.assertEqual(validateNumber("0981123456"), "595981123456")

    def test_leading_plus_is_dropped(self):
        self.assertEqual(validateNumber("+595981123456"), "595981123456")

    def test_already_normalised_number_is_unchanged(self):
        self.assertEqual(validateNumber("595981123456"), "595981123456")

    def test_separators_are_stripped(self):
        self.assertEqual(validateNumber("(0981) 123-456"), "595981123456")

    def test_uppercase_letter_o_is_read_as_zero(self):
        self.assertEqual(validateNumber("O981123456"), "595981123456")

    def test_lowercase_letter_o_is_not_converted(self):
        # Only the uppercase "O" is translated, so a lowercase one survives and
        # later makes ``Denuncia.save`` flag the report as inactive.
        self.assertEqual(validateNumber("o981123456"), "o981123456")

    def test_unicode_direction_marks_are_removed(self):
        # iOS copies phone numbers wrapped in LRO/PDF control characters.
        self.assertEqual(validateNumber("‭0981123456‬"), "595981123456")

    def test_empty_string_is_returned_untouched(self):
        self.assertEqual(validateNumber(""), "")


class SplitListTests(SimpleTestCase):
    def test_single_part_returns_whole_list(self):
        self.assertEqual(split_list([1, 2, 3]), [[1, 2, 3]])

    def test_list_is_split_into_equal_parts(self):
        self.assertEqual(
            split_list(list(range(10)), 2), [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]
        )

    def test_remainder_is_distributed_and_nothing_is_lost(self):
        parts = split_list(list(range(10)), 3)
        self.assertEqual(len(parts), 3)
        self.assertEqual([item for part in parts for item in part], list(range(10)))

    def test_empty_list_yields_empty_parts(self):
        self.assertEqual(split_list([], 2), [[], []])


class CreateThumbnailTests(SimpleTestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="listahu-thumbs-")
        self.imagepath = os.path.join(self.tmpdir, "captura.png")
        Image.new("RGB", (800, 600), (0, 128, 255)).save(self.imagepath)
        self.thumbpath = os.path.join(self.tmpdir, "captura_th.png")

    def test_thumbnail_is_created_next_to_the_original(self):
        self.assertTrue(create_thumbnail(self.imagepath, 200))
        self.assertTrue(os.path.exists(self.thumbpath))

    def test_thumbnail_keeps_the_aspect_ratio(self):
        create_thumbnail(self.imagepath, 200)
        with Image.open(self.thumbpath) as thumb:
            self.assertEqual(thumb.size, (200, 150))

    def test_existing_thumbnail_is_not_regenerated(self):
        self.assertTrue(create_thumbnail(self.imagepath, 200))
        self.assertFalse(create_thumbnail(self.imagepath, 200))

    def test_force_regenerates_an_existing_thumbnail(self):
        create_thumbnail(self.imagepath, 200)
        self.assertTrue(create_thumbnail(self.imagepath, 100, force=True))
        with Image.open(self.thumbpath) as thumb:
            self.assertEqual(thumb.size, (100, 75))

    def test_missing_source_returns_false_instead_of_raising(self):
        self.assertFalse(create_thumbnail(os.path.join(self.tmpdir, "nope.png"), 200))

    def test_non_image_source_returns_false(self):
        broken = os.path.join(self.tmpdir, "broken.png")
        with open(broken, "w") as handle:
            handle.write("not an image")
        self.assertFalse(create_thumbnail(broken, 200))


class ThumbnailAllTests(SimpleTestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="listahu-thumbs-all-")

    def test_every_image_in_the_directory_gets_a_thumbnail(self):
        for name in ("uno.png", "dos.png"):
            Image.new("RGB", (400, 400), (10, 20, 30)).save(
                os.path.join(self.tmpdir, name)
            )
        with quiet_stdout():
            thumbnail_all(self.tmpdir)
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "uno_th.png")))
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "dos_th.png")))

    def test_a_missing_directory_is_ignored(self):
        with quiet_stdout():
            thumbnail_all(os.path.join(self.tmpdir, "no-existe"))


class GetCSVTests(TestCase):
    def test_header_row_is_written(self):
        csv_text = getCSV([])
        self.assertEqual(
            csv_text.splitlines()[0],
            '"#","Numero","Tipo","Comentarios","Captura","Fecha_Denuncia"',
        )

    def test_report_is_written_with_a_one_based_index(self):
        make_denuncia(numero="0981123456", desc="spam de prueba")
        rows = getCSV(list(Denuncia.objects.all()))
        data_row = rows.splitlines()[1]
        self.assertIn("1", data_row)
        self.assertIn("595981123456", data_row)
        self.assertIn("spam de prueba", data_row)

    def test_screenshot_is_exported_as_an_absolute_url(self):
        denuncia = make_denuncia()
        csv_text = getCSV([denuncia])
        self.assertIn("https://listahu.org/media/%s" % denuncia.screenshot, csv_text)

    def test_date_is_formatted_in_the_local_timezone(self):
        denuncia = make_denuncia()
        csv_text = getCSV([denuncia])
        self.assertRegex(csv_text.splitlines()[1], r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")


class VcardTests(TestCase):
    def test_model_instances_are_exported_with_a_leading_plus(self):
        denuncia = make_denuncia(numero="0981123456")
        with quiet_stdout():
            card = vcard("Todos", [denuncia])
        self.assertIn("BEGIN:VCARD", card)
        self.assertIn("+595981123456", card)

    def test_dict_rows_from_values_queries_are_supported(self):
        with quiet_stdout():
            card = vcard("Todos", [{"numero": "595981123456"}])
        self.assertIn("+595981123456", card)

    def test_contacts_are_named_so_users_ignore_them(self):
        with quiet_stdout():
            card = vcard("Todos", [{"numero": "595981123456"}])
        self.assertIn("Lista Negra IGNORAR", card)

    def test_large_lists_are_split_into_several_cards(self):
        rows = [{"numero": "59598100%04d" % i} for i in range(250)]
        with quiet_stdout():
            card = vcard("Todos", rows)
        # One vCard per 100 entries keeps phone address books importable.
        self.assertEqual(card.count("BEGIN:VCARD"), 3)
        self.assertEqual(len(re.findall(r"^TEL", card, flags=re.MULTILINE)), 250)


class CreateVcardTests(SimpleTestCase):
    def test_single_card_holds_every_number(self):
        rows = [{"numero": "595981123456"}, {"numero": "595981654321"}]
        card = create_vcard("Todos", rows)
        self.assertEqual(card.count("BEGIN:VCARD"), 1)
        self.assertIn("+595981123456", card)
        self.assertIn("+595981654321", card)

    def test_empty_list_still_produces_a_valid_card(self):
        card = create_vcard("Todos", [])
        self.assertIn("BEGIN:VCARD", card)
        self.assertIn("END:VCARD", card)


class PrettyJsonRendererTests(SimpleTestCase):
    def test_indent_is_two_spaces(self):
        self.assertEqual(PrettyJsonRenderer().get_indent("application/json", {}), 2)
