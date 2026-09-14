"""Tests for the DRF serializers."""

from django.test import TestCase

from backend.serializers import (
    DenunciaSerializer,
    ListaSerializer,
    ListaUnicaSerializer,
)
from backend.tests.helpers import get_tipo, make_denuncia


class SerializerFieldTests(TestCase):
    def setUp(self):
        self.denuncia = make_denuncia(numero="0981123456", tipo=get_tipo("Estafa"))

    def test_denuncia_serializer_exposes_the_full_record(self):
        self.assertEqual(
            set(DenunciaSerializer(self.denuncia).data),
            {
                "id",
                "numero",
                "tipo",
                "screenshot",
                "desc",
                "check",
                "added",
                "votsi",
                "votno",
            },
        )

    def test_lista_serializer_drops_the_moderation_fields(self):
        self.assertEqual(
            set(ListaSerializer(self.denuncia).data),
            {"id", "numero", "tipo", "screenshot", "added"},
        )

    def test_lista_unica_serializer_is_the_leanest(self):
        self.assertEqual(
            set(ListaUnicaSerializer(self.denuncia).data),
            {"id", "numero", "tipo", "added"},
        )

    def test_tipo_is_rendered_as_its_title(self):
        self.assertEqual(DenunciaSerializer(self.denuncia).data["tipo"], "Estafa")

    def test_number_is_serialised_normalised(self):
        self.assertEqual(
            DenunciaSerializer(self.denuncia).data["numero"], "595981123456"
        )

    def test_tipo_is_read_only(self):
        # ``SlugRelatedField(read_only=True)`` means the API cannot set a type.
        self.assertTrue(DenunciaSerializer().fields["tipo"].read_only)
