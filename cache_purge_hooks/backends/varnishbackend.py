import varnish
import logging
from django.conf import settings

#STUB config options here
VARNISH_HOST = settings.VARNISH_HOST
VARNISH_PORT = settings.VARNISH_PORT
VARNISH_DEBUG = settings.DEBUG
VARNISH_SECRET = settings.VARNISH_SECRET or None
VARNISH_SITE_DOMAIN = settings.VARNISH_SITE_DOMAIN or '.*'

class VarnishManager(object):
	def __init__(self):
		varnish_url = "{host}:{port}".format(host=VARNISH_HOST, port=VARNISH_PORT)
		self.handler = varnish.VarnishHandler(varnish_url, secret=VARNISH_SECRET)

	def __send_command(self, command):
		if VARNISH_DEBUG:
			logging.info("unrun cache command (debug on): {0}".format(command))
		else:
			self.handler.fetch(command.encode('utf-8'))

	def close(self):
		self.handler.close()

	def purge(self, command):
		cmd = r'ban req.http.host ~ "{host}" && req.url ~ "{url}"'.format(
			host = VARNISH_SITE_DOMAIN.encode('ascii'),
			url = command.encode('ascii'),
		)
		self.__send_command(cmd)
		
	def purge_all(self):
		return self.expire('.*')

