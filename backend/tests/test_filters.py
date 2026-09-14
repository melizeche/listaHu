"""Tests for :class:`backend.filters.DenunciaFilter`."""

import datetime

from django.test import TestCase
from django.utils import timezone

from backend.filters import DenunciaFilter
from backend.models import Denuncia
from backend.tests.helpers import get_tipo, make_denuncia


def as_input(value):
    """Render a datetime the way the ``added_*`` filters expect it.

    The filters clean their input with the active locale's
    ``DATETIME_INPUT_FORMATS``, which means local time and a space (not a
    "T") between the date and the time.
    """
    return timezone.localtime(value).strftime("%Y-%m-%d %H:%M:%S")


class DenunciaFilterTests(TestCase):
    def setUp(self):
        self.spam = make_denuncia(numero="0981111111", tipo=get_tipo("SPAM"))
        self.estafa = make_denuncia(numero="0982222222", tipo=get_tipo("Estafa"))

    def filtered(self, params):
        return list(DenunciaFilter(params, queryset=Denuncia.objects.all()).qs)

    def test_no_parameters_returns_everything(self):
        self.assertEqual(len(self.filtered({})), 2)

    def test_filter_by_tipo_slug(self):
        self.assertEqual(self.filtered({"tipo": get_tipo("SPAM").slug}), [self.spam])

    def test_unknown_tipo_slug_returns_nothing(self):
        self.assertEqual(self.filtered({"tipo": "no-existe"}), [])

    def test_filter_by_numero_is_a_partial_match(self):
        self.assertEqual(self.filtered({"numero": "981111"}), [self.spam])

    def test_filter_by_full_normalised_numero(self):
        self.assertEqual(self.filtered({"numero": "595981111111"}), [self.spam])

    def test_filter_by_id_range(self):
        self.assertEqual(self.filtered({"id_from": self.estafa.pk}), [self.estafa])
        self.assertEqual(self.filtered({"id_to": self.spam.pk}), [self.spam])

    def test_filter_by_added_from_is_inclusive(self):
        self.assertEqual(
            len(self.filtered({"added_from": as_input(self.spam.added)})), 2
        )

    def test_filter_by_added_to_is_exclusive(self):
        self.assertEqual(self.filtered({"added_to": as_input(self.spam.added)}), [])

    def test_filter_by_added_window(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        self.assertEqual(len(self.filtered({"added_to": as_input(tomorrow)})), 2)

    def test_date_only_input_is_accepted(self):
        today = timezone.localtime(timezone.now()).strftime("%Y-%m-%d")
        self.assertEqual(len(self.filtered({"added_from": today})), 2)

    def test_iso_8601_input_is_accepted(self):
        # Django also cleans ISO-8601 timestamps (with a "T" and a UTC offset)
        # on top of the locale's ``DATETIME_INPUT_FORMATS``, so the exclusive
        # ``added_to`` bound really does apply here.
        self.assertEqual(self.filtered({"added_to": self.spam.added.isoformat()}), [])

    def test_unparseable_date_is_silently_ignored(self):
        # django-filter drops values the form cannot clean instead of raising,
        # so a bogus timestamp simply returns the unfiltered queryset.
        self.assertEqual(len(self.filtered({"added_to": "no-es-una-fecha"})), 2)

    def test_filter_by_check_flag(self):
        Denuncia.objects.filter(pk=self.spam.pk).update(checked=True)
        self.assertEqual(self.filtered({"check": "true"}), [self.spam])
        self.assertEqual(self.filtered({"check": "false"}), [self.estafa])
