#!/usr/bin/python

import SocketServer
import sys
import threading

import localconfig

class SpamLocalServer(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        import os
        received_data = self.request.recv(1024).strip()
        received_data = received_data.replace('GET /', '')
        received_data = received_data[:received_data.find('HTTP')-1]
        
        local_config = localconfig.credentiales()
        
        operation = received_data[:received_data.find('?')]
        file_path = received_data.replace(operation + '?', '')
        local_repository = local_config.repository
        print (operation, file_path, local_repository)
        if operation == 'open':
            # open file
            
            # get file extension
            file_ext = (file_path[file_path.rfind('.')+1:]).lower()
            print (file_ext)
            if file_ext in ['shk']:
                # open with blender
                os.system('shake %s' % os.path.join(local_repository, file_path))
                
            if file_ext in ['blend']:
                # open with blender
                os.system('blender %s' % os.path.join(local_repository, file_path))
                
            if file_ext in ['jpg', 'png', 'xcf', 'tif']:
                # open with gimp
                os.system('gimp %s' % os.path.join(local_repository, file_path))
                
            if file_ext in ['mov', 'mp4', 'avi', 'm2v', 'mts', 'mxf']:
                # open with vlc
                os.system('vlc -f --play-and-exit %s' % os.path.join(local_repository, file_path))
                
            #self.request.send(file_path)
            self.request.send('')
            
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = "localhost", 8083
    server = ThreadedTCPServer((HOST, PORT), SpamLocalServer)
    
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    #server_thread.daemon = True
    server_thread.start()
    #server.serve_forever()
