import os
import tornado.websocket
import streaming_manager

class AudioHandler( tornado.websocket.WebSocketHandler ):
    
    def open( self ):
        self.streamer = None
        print( 'new connection' )

    def on_message(self, data) :
        if 'm:' == str( data[0] + data[1] ) :
            rate, is_encoded, op_rate, op_frm_dur = [int(i) for i in data[2:].split(',')]
            self.rate = rate
            self.streamer = streaming_manager.StreamingManager(rate)
        else:
            self.streamer.register_data(data)

    def on_close( self ):

        print( 'connection closed' )

class MainHandler( tornado.web.RequestHandler ):
    def get( self ):
        self.render( "www/index.html" )

app = tornado.web.Application( [
    ( r'/ws', AudioHandler ),
    ( r'/', MainHandler ),
    ( r'/(.*)', tornado.web.StaticFileHandler, { 'path' : './www' } )
] )

http_server = tornado.httpserver.HTTPServer( app )
http_server.listen( int( os.environ.get( 'PORT', 8888 ) ) )
print( 'http server started' )
tornado.ioloop.IOLoop.instance().start()
