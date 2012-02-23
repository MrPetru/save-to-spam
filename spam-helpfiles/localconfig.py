import os
import sys

if sys.version_info[0] == 3:
    import configparser
else:
    import ConfigParser as configparser

""" hold local configuration """


class credentiales():

    def __init__(self):
        """ get the curent user data from spamconfig fiel """
        import os
        
        config = configparser.ConfigParser()
        username = os.getenv('USER')
        path_to_config = os.path.join('/home', username, 'spamconfig.ini')
        result = config.read(path_to_config)
        if not sys.version_info[0] == 3:
            config = {'DEFAULT': dict(config.items('DEFAULT'))}
        if result == []:
            self.user = None
            self.paswd = None
            self.host = None
            self.repository = None
            self.adminname = None
            self.adminpassword = None
        else:
            self.user = config['DEFAULT']['username']
            self.paswd = config['DEFAULT']['password']
            self.host = config['DEFAULT']['host']
            self.repository = config['DEFAULT']['repository']
            self.adminname = config['DEFAULT']['adminname']
            self.adminpassword = config['DEFAULT']['adminpassword']
