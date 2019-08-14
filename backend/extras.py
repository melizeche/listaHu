import vobject
import csv
import glob

from io import StringIO
from os import path
from PIL import Image
from django.utils import timezone
from rest_framework.renderers import JSONRenderer


def validateNumber(number: str) -> str:
    number = number.replace('\u202d','').replace('\u202c','')
    number = number.replace(" ", "")
    number = number.replace("-", "")
    number = number.replace(")", "")
    number = number.replace("(", "")
    number = number.replace("O", "0")
    if number.startswith('09'):
        new = "5959" + number[2:]
    elif number.startswith('+'):
        new = number[1:]
    else:
        new = number

    return new


def getCSV(datos):
    si = StringIO()
    writer = csv.writer(si, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(['#', 'Numero', 'Tipo', 'Comentarios',
                     'Captura', 'Fecha_Denuncia'])
    for count, fila in enumerate(datos):
        writer.writerow(
            [count + 1,
             fila.numero,
             fila.tipo.titulo,
             fila.desc,
             'https://listahu.org/media/%s' % fila.screenshot,
             fila.added.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M")])
    return si.getvalue()


def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts]
            for i in range(wanted_parts)]


def vcard(name, lista):
    count = 1
    c = 0
    separado = list(zip(*[iter(list(lista))] * 200))
    partes = len(list(lista)) // 100
    print((partes + 1))
    separado = split_list(list(lista), partes + 1)
    jj = ""
    for sep in separado:
        print(count)
        j = vobject.vCard()
        o = j.add('fn')
        o.value = "Lista Negra IGNORAR" + str(count)

        o = j.add('n')
        o.value = vobject.vcard.Name(
            family='IGNORAR', given='Lista Negra' + str(count))

        for i, num in enumerate(sep):
            c += 1

            o = j.add('tel')
            o.type_param = "cell"
            if isinstance(num, dict):
                o.value = "+" + num['numero']
            else:
                o.value = "+" + num.numero
        count += 1
        jj += j.serialize()
        print(("vCard" + str(count) + " " + str(c) + " numeros"))
        c = 0

    return (jj)


def create_vcard(name, lista):
    count = 0
    card = vobject.vCard()
    obj = card.add('fn')
    obj.value = "Lista Negra IGNORAR" + str(count)

    obj = card.add('n')
    obj.value = vobject.vcard.Name(
        family='IGNORAR', given='Lista Negra' + str(count))

    for i, num in enumerate(lista):
        count += 1
        obj = card.add('tel')
        obj.type_param = "cell"
        obj.value = "+" + num['numero']
    return (card.serialize())


def create_thumbnail(imagepath: str, basewidth: int, force=False) -> bool:
    thumbfilename = "%s_th%s" % (path.splitext(
        imagepath)[0], path.splitext(imagepath)[1])
    if not path.exists(thumbfilename) or force:
        try:
            img = Image.open(imagepath)
            wpercent = (basewidth / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)
            thumbfilename = "%s_th%s" % (path.splitext(
                imagepath)[0], path.splitext(imagepath)[1])
            img.save(thumbfilename)
            return True
        except:
            return False
    return False


def thumbnail_all(directory: str):
    if path.isdir(directory):
        for infile in glob.glob(directory + "/*.*"):
            print((create_thumbnail(infile, 200), infile))


class PrettyJsonRenderer(JSONRenderer):
    def get_indent(self, accepted_media_type, renderer_context):
        return 2