# -*- encoding: utf-8 -*-
import vobject

def validateNumber(number):

		if number.startswith('09'):
			new = "5959" + number[2:]
		elif number.startswith('+'):
			new = number[1:]
		else:
			new = number

		return new

def vcard(name,lista):

	j = vobject.vCard()
	o = j.add('fn')
	o.value = "Lista Negra IGNORAR"

	o = j.add('n')
	o.value = vobject.vcard.Name( family='IGNORAR', given='Lista Negra' )

	for i,num in enumerate(lista):

		o = j.add('tel')
		o.type_param = "cell"
		o.value = "+"+num.numero


	return(j.serialize())