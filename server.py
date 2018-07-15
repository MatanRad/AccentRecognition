import os
import tornado.websocket
import streaming_manager
import json


# WebSocket handler for audio data.
class AudioHandler(tornado.websocket.WebSocketHandler):
    # initiate streamer
    def open(self):
        self.streamer = None
        print('new connection')

    # respond to the client that sent a message to the WebSocket
    def respond(self, msg):
        self.write_message(msg)

    # on message received from client
    def on_message(self, data):
        # if the message starts with 'm:' then it is initializing the streamer
        if 'm:' == str(data[0] + data[1]):
            rate, is_encoded, op_rate, op_frm_dur = [int(i) for i in data[2:].split(',')]
            self.rate = rate
            # init streamer, define the network file and the sample rate.
            self.streamer = streaming_manager.StreamingManager(rate, "us_ar.h5", self.respond)
            # tell the clients the names of the accents to show.
            self.respond(json.dumps(["American", "Arabic"]))
        else:
            # data has been receieved, handle it.
            self.streamer.register_data(data)

    def on_close(self):

        print('connection closed')

# main handler for showing a webpage.
class MainHandler( tornado.web.RequestHandler ):
    def get( self ):
        self.render( "www/index.html" )

# our web app. contains a audio handler (websocket), main handler for our main website and a file handler for anything
# else.
app = tornado.web.Application( [
    ( r'/ws', AudioHandler ),
    ( r'/', MainHandler ),
    ( r'/(.*)', tornado.web.StaticFileHandler, { 'path' : './www' } )
] )

# init our server and start it.
http_server = tornado.httpserver.HTTPServer(app)
http_server.listen( int( os.environ.get( 'PORT', 8888 ) ) )
print( 'http server started' )
tornado.ioloop.IOLoop.instance().start()
