import socket
from xml.dom.minidom import parse
import cStringIO
import logging

import httplib
from httplib import HTTPConnection, HTTPS_PORT
import ssl


class SoapService(object):
    def __init__(self, host, host_s2s, url, debuglevel=0):
        self.host = host
        self.host_s2s = host_s2s
        self.url = url
        httplib.HTTPConnection.debuglevel = debuglevel

    def SOAP_post(self, xml, action):
        """Handles making the SOAP request"""
        h = HTTPSConnection(self.host_s2s)
        headers = {
            'Host': self.host_s2s,
            'Content-Type': 'text/xml; charset=utf-8',
            'Content-Length': len(xml),
            'SOAPAction': '"%s"' % (action,),
        }

        # BancaSella requires GET
        logger = logging.getLogger('BancaSella:')

        logger.info('host: %s\n\nurl: %s\n\nXML: %s\n\nHeaders: %s\n\n' % (self.host_s2s, self.url, xml, str(headers)))

        print self.host_s2s, self.url, xml, str(headers)
        h.request('POST', self.url, body = xml, headers = headers)

        resp = h.getresponse()
        if resp.status != 200:
            raise ValueError('Error connecting: %s, %s' % (resp.status, resp.reason))
        return resp  # return file-like object


class GestPaySoap(SoapService):
    def encrypt(self, shop_login, uic_code, amount, transaction_id):
        logger = logging.getLogger('BancaSella:')
        logger.info(" -- Encrypt")

        request = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ecom="https://ecomm.sella.it/">
   <soapenv:Header/>
   <soapenv:Body>
      <ecom:Encrypt>
         <ecom:shopLogin>%s</ecom:shopLogin>
         <ecom:uicCode>%s</ecom:uicCode>
         <ecom:amount>%s</ecom:amount>
         <ecom:shopTransactionId>%s</ecom:shopTransactionId>
      </ecom:Encrypt>
   </soapenv:Body>
</soapenv:Envelope>""" % (shop_login, uic_code, amount, transaction_id)
        # 2-call soap

        f = self.SOAP_post(request, "https://ecomm.sella.it/Encrypt")
        doc = parse(f)
        # 3-get the result
        response = doc.getElementsByTagName('TransactionResult')[0].firstChild.data
        if response != 'OK':
            return 'SOAP Error: %s' % doc.getElementsByTagName('ErrorCode')[0].firstChild.data

        # NO S2S
        return 'https://%s/pagam/pagam.aspx?a=%s&b=%s' % (self.host, shop_login, doc.getElementsByTagName('CryptDecryptString')[0].firstChild.data)

    def decrypt(self, shop_login, gpstring):
        logger = logging.getLogger('BancaSella:')
        logger.info(" -- Encrypt")
        request = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ecom="https://ecomm.sella.it/">
   <soapenv:Header/>
   <soapenv:Body>
      <ecom:Decrypt>
         <ecom:shopLogin>%s</ecom:shopLogin>
         <ecom:CryptedString>%s</ecom:CryptedString>
      </ecom:Decrypt>
   </soapenv:Body>
</soapenv:Envelope>
""" % (shop_login, gpstring)

        # 2-call soap
        f = self.SOAP_post(request, "https://ecomm.sella.it/Decrypt")
        xml = f.read()
        f.close()

        fake_response = cStringIO.StringIO()
        fake_response.write(xml)
        fake_response.seek(0)
        doc = parse(fake_response)
        fake_response.close()

        # 3-get the result

        # import pdb; pdb.set_trace()

        data = {}

        response = doc.getElementsByTagName('TransactionResult')[0].firstChild.data
        if response == 'KO':
            data['result'] = response
            try:
                data['order_number'] = doc.getElementsByTagName('ShopTransactionID')[0].firstChild.data
            except:
                data['clab_status'] = False
                return data

        if response == 'OK':
            data['result'] = response
            data['order_number'] = doc.getElementsByTagName('ShopTransactionID')[0].firstChild.data
            data['xml'] = xml

        return data



class HTTPSConnection(HTTPConnection):
    "This class allows communication via SSL."
    default_port = HTTPS_PORT

    def __init__(self, host, port=None, key_file=None, cert_file=None,
            strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
            source_address=None):
        HTTPConnection.__init__(self, host, port, strict, timeout)
        self.key_file = key_file
        self.cert_file = cert_file

    def connect(self):
        "Connect to a host on a given (SSL) port."
        sock = socket.create_connection((self.host, self.port),
                self.timeout)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        # this is the only line we modified from the httplib.py file
        # we added the ssl_version variable
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_TLSv1)

#now we override the one in httplib
httplib.HTTPSConnection = HTTPSConnection
# ssl_version corrections are done