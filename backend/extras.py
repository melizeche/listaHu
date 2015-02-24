# -*- encoding: utf-8 -*-
import vobject
import csv, datetime, unicodedata, cStringIO
from django.utils import timezone

def validateNumber(number):
		number = number.replace(" ", "")
		if number.startswith('09'):
			new = "5959" + number[2:]
		elif number.startswith('+'):
			new = number[1:]
		else:
			new = number

		return new

def getCSV(datos):
	si = cStringIO.StringIO()    
	writer = csv.writer(si,dialect='excel')
	writer.writerow(['#', 'Numero', 'Tipo', 'Comentarios','Captura','Fecha_Denuncia'])
	for count,fila in enumerate(datos):
		writer.writerow([count+1, fila.numero, unicodedata.normalize('NFKD', fila.tipo.titulo).encode('ASCII', 'ignore'), 
				unicodedata.normalize('NFKD', fila.desc).encode('ASCII', 'ignore'), 'http://listahu.org/media/%s' % fila.screenshot, fila.added.astimezone(timezone.get_current_timezone()).strftime("%Y/%m/%d %H:%M")])
	return si.getvalue()

def vcard(name,lista):

	j = vobject.vCard()
	o = j.add('fn')
	o.value = "Lista Negra IGNORAR"

	o = j.add('n')
	o.value = vobject.vcard.Name( family='IGNORAR', given='Lista Negra' )

	for i,num in enumerate(lista):
		
		o = j.add('tel')
		o.type_param = "cell"
		if isinstance(num, dict):
			o.value = "+"+num['numero']
		else:
			o.value = "+"+num.numero

	return(j.serialize())