#-*- coding: utf-8 -*-

import urllib
import urllib2

def pegar_coordenadas(self):
#   if not self.latitude:
# try:
    q_string = u'%s, %s' % (self.endereco, self.localizacao.cidade.titulo)
    data = {
        'q': q_string.encode('utf-8'),
        'output': 'csv',
        'key': "ABQIAAAAvDjVyyEeeRdwFXFHhnQaxhSL7X9eFkihBtf85CDE1ZBEpqznOxSdexQAkkAhOhnHrgry8oBLBX--XA"
    }
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers={'User-Agent':user_agent,}
    url = urllib.urlencode(data)
    request = urllib2.Request("http://maps.google.com/maps/geo?" + url, None, headers)
    pagina = urllib2.urlopen(request)
    corta = pagina.read().split(',')

    self.latitude = corta[2]
    self.longitude = corta[3]
    self.save()
    #  except urllib2.URLError:
    #      pass

