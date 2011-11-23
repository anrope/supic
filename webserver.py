from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.web.wsgi import WSGIResource
from twisted.web.static import File
from twisted.internet import reactor

import parse_query

resource = File('./')
resource.putChild('parse_query', WSGIResource(reactor, reactor.getThreadPool(), parse_query.supic))

factory = Site(resource)
reactor.listenTCP(8888, factory)
reactor.run()