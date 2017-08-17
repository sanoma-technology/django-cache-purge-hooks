import logging
import subprocess

from django.conf import settings

logger = logging.getLogger('django.cache_purge_hooks')

VARNISHADM_HOST = getattr(settings, 'VARNISHADM_HOST', 'localhost')
VARNISHADM_PORT = getattr(settings, 'VARNISHADM_PORT', 6082)
VARNISHADM_SECRET = getattr(settings, 'VARNISHADM_SECRET', '/etc/varnish/secret')
VARNISHADM_SITE_DOMAIN = getattr(settings, 'VARNISHADM_SITE_DOMAIN', '.*')
VARNISHADM_BIN = getattr(settings, 'VARNISHADM_ADM_BIN', '/usr/bin/varnishadm')


class VarnishManager(object):
    def purge(self, url):
        command = 'ban req.http.host ~ "{host}" && req.url ~ "{url}"'.format(
            host=VARNISHADM_SITE_DOMAIN.encode('ascii'),
            url=url.encode('ascii'),
        )
        self.send_command(command)

    def purge_all(self):
        self.purge('.*')

    def send_command(self, command):
        if not isinstance(VARNISHADM_HOST, list):
            varnish_hosts = []
            varnish_hosts.append(VARNISHADM_HOST)
        else:
            varnish_hosts = VARNISHADM_HOST

        for varnish_host in varnish_hosts:
            args = [VARNISHADM_BIN, '-S', VARNISHADM_SECRET, '-T', varnish_host + ':' + str(VARNISHADM_PORT), command]
            try:
                logger.debug('Purging: {} {}'.format(varnish_host, command))
                #  use check_output so that prints returned by varnishadm aren't logged as empty
                # lines
                subprocess.check_output(args)
            except subprocess.CalledProcessError as error:
                logger.error('Command "{0}" returned {1}'.format(' '.join(args), error.returncode))
            else:
                logger.debug('Command "{0}" executed successfully'.format(' '.join(args)))
