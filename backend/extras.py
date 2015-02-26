# -*- encoding: utf-8 -*-
import vobject
import csv, datetime, unicodedata, cStringIO
from django.utils import timezone

def validateNumber(number):
		number = number.replace(" ", "")
		number = number.replace("-", "")
		number = number.replace(")", "")
		number = number.replace("(", "")
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

def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ]

def vcard(name,lista):
	count = 1
	c = 0
	separado = zip(*[iter(list(lista))]*200)
	partes = len(list(lista))/150
	print partes + 1
	separado = split_list(list(lista),partes+1)
	jj=""
	for sep in separado:	
		print count
		j = vobject.vCard()
		o = j.add('fn')
		o.value = "Lista Negra IGNORAR" + str(count)

		o = j.add('n')
		o.value = vobject.vcard.Name( family='IGNORAR', given='Lista Negra' + str(count) )

		for i,num in enumerate(sep):
			c+=1
			
			o = j.add('tel')
			o.type_param = "cell"
			if isinstance(num, dict):
				o.value = "+"+num['numero']
			else:
				o.value = "+"+num.numero
		count += 1
		jj += j.serialize()
		print "vCard" + str(count)+ " " + str(c) + " numeros"
		c=0


	return(jj)

def vcard2(name,lista):
	count = 0
	j = vobject.vCard()
	o = j.add('fn')
	o.value = "Lista Negra IGNORAR" + str(count)

	o = j.add('n')
	o.value = vobject.vcard.Name( family='IGNORAR', given='Lista Negra' + str(count) )

	for i,num in enumerate(lista):
		count += 1
		o = j.add('tel')
		o.type_param = "cell"
		if isinstance(num, dict):
			o.value = "+"+num['numero']
		else:
			o.value = "+"+num.numero

		print count
	return(j.serialize())