__author__ = 'W0nk0'

import cherrypy

#<meta http-equiv="refresh" content="5; URL=http://de.selfhtml.org/">
class MiniWebServer(object):

    def __init__(self):
        self._text = "Running"
        self._text2 = ""
        #self.srv =
        conf = {
            'global': {
                'server.socket_host': '0.0.0.0',
                'server.socket_port': 8080,
                #'environment': 'embedded',
            },
            #'/': {
            #    'tools.response_headers.headers': [('Content-Type', 'text/plain')]
            #}
        }
        cherrypy.tree.mount(self,'',conf)
        cherrypy.config.update(conf)
        cherrypy.engine.start()


    #def __init__(self):
    #    self._text = "Running"
    @cherrypy.expose
    def index(self):
        cherrypy.response.headers['refresh'] = "3; URL=/"
        return [self.wrap(self._text, self._text2 )]

    def wrap(self, text, text2=""):
        start = '<body style="background-color:black">'
        start += '<br><h1 style="color:orange">'
        end1 = '</h1>'
        start2 = '<br><h2 style="color:green">'
        end2 = '</h2>'
        end = '</body>'
        total = start + text + end1

        if text2:
            total += start2 + text2 + end2

        return total+end

    def stop(self):
        cherrypy.engine.stop()

    @property
    def main(self):
        return self._text

    @main.setter
    def main(self,new_text):
        self._text = new_text

    @property
    def secondary(self):
        return self._text2

    @secondary.setter
    def secondary(self,new_text):
        self._text2 = new_text

    #text.exposed = True
    #index.exposed = True



if __name__ == '__main__':
    conf = {
        'global': {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 80,
        },
        '/': {
            'tools.response_headers.headers': [('Content-Type', 'text/plain')]
        }
    }

    srv = MiniWebServer()
    srv.text = "Running!"
    print "Run"
    #cherrypy.tree.mount(srv,'',conf)
    srv.text = "Started"
    #cherrypy.engine.start()
    srv.text = "Sleeping"
    from time import sleep
    print "Sleep"
    sleep(10)
    srv.text = "Sleeping more"
    sleep(10)
    #cherrypy.quickstart(MiniWebServer(),config=conf)


