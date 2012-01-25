#import bpy
from . import localconfig, spamclient

""" all functions that help as to login into spam """

class logindata():
        
    def connect(self):
        pass
        
    def __init__(self):
        self.configdata = localconfig.credentiales()
        self.name = self.configdata.user
        self.paswd = self.configdata.paswd
        self.repository = self.configdata.repository
        self.conn = spamclient.Client(self.configdata.host)
        self.conn.login(self.name, password=self.paswd)
        
        self.adminconn = spamclient.Client(self.configdata.host)
        self.adminconn.login(self.configdata.adminname, password=self.configdata.adminpassword)
