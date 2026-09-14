"""Shared helpers for the ListaHũ test suite."""

import contextlib
import io

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection

from backend.models import Denuncia, Tipo


def make_image_file(name="captura.png", size=(400, 300), color=(255, 0, 0)):
    """Build an in-memory PNG suitable for an ``ImageField``."""
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/png")


def get_tipo(titulo="SPAM"):
    """Return one of the ``Tipo`` rows seeded by migration ``0002_seed_tipo``."""
    return Tipo.objects.get(titulo=titulo)


def make_denuncia(numero="0981123456", tipo=None, **kwargs):
    """Create a saved ``Denuncia`` with a real (tiny) screenshot attached."""
    kwargs.setdefault("screenshot", make_image_file())
    kwargs.setdefault("desc", "Mensaje de prueba")
    return Denuncia.objects.create(numero=numero, tipo=tipo or get_tipo(), **kwargs)


@contextlib.contextmanager
def quiet_stdout():
    """Silence the ``print`` calls inside ``backend.extras.vcard``."""
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def supports_distinct_on_fields():
    """``DISTINCT ON`` (and the raw SQL in ``ListaUnicaViewSet``) is PostgreSQL only."""
    return connection.features.can_distinct_on_fields
