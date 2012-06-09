#
# generated by mrClientMaker ((c)Lorenzo Pierfederici <lpierfederici@gmail.com>)
#
"""Standalone SPAM client."""

import getpass, cookielib, urllib, urllib2, json, os, stat, mimetools, mimetypes
from cStringIO import StringIO

def prep_data(args, **kwargs):
    args.pop('self', None)
    args.update(kwargs)
    return args

def encode_params(params):
    for key, value in params.iteritems():
        if value is not None:
            params[key] = value
        else:
            params[key] = ''
    return urllib.urlencode(params, True)


# 02/2006 Will Holcomb <wholcomb@gmail.com>
# 7/26/07 Slightly modified by Brian Schneider: support unicode files
# 01/2010 Lorenzo Pierfederici <lpierfederici@gmail.com>
class MultipartPostHandler(urllib2.BaseHandler):
    """Enables the use of multipart/form-data for posting forms.

    Inspirations:
        * http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306
        * urllib2_file: Fabien Seisen <fabien@seisen.org>

    Example::
        >>> import urllib2, cookielib
        >>> cookies = cookielib.CookieJar()
        >>> opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies),
        ...                                                 MultipartPostHandler)
        >>> params = dict(username='bob', password='riviera', file=open('filename', 'rb'))
        >>> opener.open('http://wwww.bobsite.com/upload/', params)
    """
    handler_order = urllib2.HTTPHandler.handler_order - 10 # needs to run first

    def http_request(self, request):
        data = request.get_data()
        if data is None or isinstance(data, basestring):
            return request
        files = [v for v in data.itervalues() if isinstance(v, file)]
        if not files:
            for v in data.itervalues():
                if isinstance(v, list):
                    files = v
        if files:
            boundary, data = self.multipart_encode(data.iteritems())
            contenttype = 'multipart/form-data; boundary=%s' % boundary
            request.add_header('Content-Type', contenttype)
        else:
            data = encode_params(data)

        request.add_data(data)
        return request

    def multipart_encode(self, values, boundary=None, buf=None):
        if boundary is None:
            boundary = mimetools.choose_boundary()
        if buf is None:
            buf = StringIO()

        for(key, value) in values:
            if isinstance(value, file):
                file_size = os.fstat(value.fileno())[stat.ST_SIZE]
                dirname, filename = os.path.split(value.name)
                contenttype = (mimetypes.guess_type(filename)[0] or
                                                    'application/octet-stream')
                buf.write('--%s\r\n' % boundary)
                buf.write('Content-Disposition: form-data; name="%s"; '
                                        'filename="%s"\r\n' % (key, filename))
                buf.write('Content-Type: %s\r\n' % contenttype)
                buf.write('Content-Length: %s\r\n' % file_size)
                value.seek(0)
                buf.write('\r\n' + value.read() + '\r\n')
            elif isinstance(value, list):
                for f in value:
                    if isinstance(f, file):
                        file_size = os.fstat(f.fileno())[stat.ST_SIZE]
                        dirname, filename = os.path.split(f.name)
                        contenttype = (mimetypes.guess_type(filename)[0] or
                                                            'application/octet-stream')
                        buf.write('--%s\r\n' % boundary)
                        buf.write('Content-Disposition: form-data; name="%s"; '
                                                'filename="%s"\r\n' % (key, filename))
                        buf.write('Content-Type: %s\r\n' % contenttype)
                        buf.write('Content-Length: %s\r\n' % file_size)
                        f.seek(0)
                        buf.write('\r\n' + f.read() + '\r\n')
                        
            else:
                buf.write('--%s\r\n' % boundary)
                buf.write('Content-Disposition: form-data; name="%s"' % key)
                buf.write('\r\n\r\n' + str(value) + '\r\n')
        buf.write('--' + boundary + '--\r\n\r\n')
        buf = buf.getvalue()
        return boundary, buf

    https_request = http_request


class Category(object):
    """Category calls."""
    def __init__(self, openfunc):
        self.open = openfunc
    
    
    def get(self, name):
        """This method is currently unused, but is needed for the 
        RESTController to work.

        Returns:
            ``category``
        """
        data = prep_data(locals(), )
        
        params = encode_params(data)
        result = self.open('category/get_one.json?%s' % params)
        
        return json.loads(result.read())['category']

    
    def new(self, category_id, ordering=None, naming_convention=None):
        """Create a new category

        Returns:
            ``category``
        """
        data = prep_data(locals(), )
        
        result = self.open('category.json', data)
        
        return json.loads(result.read())['category']

    
    def edit(self, category_id, ordering=None, naming_convention=None):
        """Edit a category

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='PUT')
        
        result = self.open('category.json', data)
        
        return result

    
    def delete(self, category_id):
        """Delete a category.
        
        Only delete the category record from the common db, all the assets
        in this category will be orphaned, and must be removed manually.
        

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='DELETE')
        
        result = self.open('category.json', data)
        
        return result



class Project(object):
    """Project calls."""
    def __init__(self, openfunc):
        self.open = openfunc
    
    
    def get(self, proj):
        """Return a `tabbed` page for project tabs.

        Returns:
            ``project``
        """
        data = prep_data(locals(), )
        
        params = encode_params(data)
        result = self.open('project/get_one.json?%s' % params)
        
        return json.loads(result.read())['project']

    
    def new(self, proj, name=None, description=None):
        """Create a new project

        Returns:
            ``project``
        """
        data = prep_data(locals(), )
        
        result = self.open('project.json', data)
        
        return json.loads(result.read())['project']

    
    def edit(self, proj, name=None, description=None):
        """Edit a project

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='PUT')
        
        result = self.open('project.json', data)
        
        return result

    
    def delete(self, proj):
        """Delete a project.
        
        Only delete the project record from the common db, the project
        repository must be removed manually.
        (This should help prevent awful accidents) ;)
        

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='DELETE')
        
        result = self.open('project.json', data)
        
        return result

    
    def archive(self, proj):
        """Archive a project

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='ARCHIVE')
        
        result = self.open('project.json', data)
        
        return result

    
    def activate(self, proj):
        """Activate a project

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='ACTIVATE')
        
        result = self.open('project.json', data)
        
        return result



class Shot(object):
    """Shot calls."""
    def __init__(self, openfunc):
        self.open = openfunc
    
    
    def get(self, proj, sc, sh):
        """Return a `tabbed` page for shot tabs.

        Returns:
            ``shot``
        """
        data = prep_data(locals(), )
        
        params = encode_params(data)
        result = self.open('shot/get_one.json?%s' % params)
        
        return json.loads(result.read())['shot']

    
    def new(self, proj, sc, sh, description=None, action=None, frames=None, handle_in=None, handle_out=None):
        """Create a new shot

        Returns:
            ``shot``
        """
        data = prep_data(locals(), )
        
        result = self.open('shot.json', data)
        
        return json.loads(result.read())['shot']

    
    def edit(self, proj, sc, sh, description=None, action=None, frames=None, handle_in=None, handle_out=None):
        """Edit a shot

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='PUT')
        
        result = self.open('shot.json', data)
        
        return result

    
    def delete(self, proj, sc, sh):
        """Delete a shot.
        
        Only delete the shot record from the db, the shot directories must be
        removed manually.
        (This should help prevent awful accidents) ;)
        

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='DELETE')
        
        result = self.open('shot.json', data)
        
        return result



class Libgroup(object):
    """Libgroup calls."""
    def __init__(self, openfunc):
        self.open = openfunc
    
    
    def get(self, proj, libgroup_id):
        """Return a `tabbed` page for libgroup tabs.

        Returns:
            ``libgroup``
        """
        data = prep_data(locals(), )
        
        params = encode_params(data)
        result = self.open('libgroup/get_one.json?%s' % params)
        
        return json.loads(result.read())['libgroup']

    
    def new(self, proj, parent_id, name, description=None):
        """Create a new libgroup

        Returns:
            ``libgroup``
        """
        data = prep_data(locals(), )
        
        result = self.open('libgroup.json', data)
        
        return json.loads(result.read())['libgroup']

    
    def edit(self, proj, libgroup_id, description=None):
        """Edit a libgroup

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='PUT')
        
        result = self.open('libgroup.json', data)
        
        return result

    
    def delete(self, proj, libgroup_id):
        """Delete a libgroup.
        
        Only delete the libgroup record from the db, the scene directories must
        be removed manually.
        (This should help prevent awful accidents) ;)
        

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='DELETE')
        
        result = self.open('libgroup.json', data)
        
        return result



class Scene(object):
    """Scene calls."""
    def __init__(self, openfunc):
        self.open = openfunc
    
    
    def get(self, proj, sc):
        """Return a `tabbed` page for scene tabs.

        Returns:
            ``scene``
        """
        data = prep_data(locals(), )
        
        params = encode_params(data)
        result = self.open('scene/get_one.json?%s' % params)
        
        return json.loads(result.read())['scene']

    
    def new(self, proj, sc, description=None):
        """Create a new scene

        Returns:
            ``scene``
        """
        data = prep_data(locals(), )
        
        result = self.open('scene.json', data)
        
        return json.loads(result.read())['scene']

    
    def edit(self, proj, sc, description=None):
        """Edit a scene

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='PUT')
        
        result = self.open('scene.json', data)
        
        return result

    
    def delete(self, proj, sc):
        """Delete a scene.
        
        Only delete the scene record from the db, the scene directories must be
        removed manually.
        (This should help prevent awful accidents) ;)
        

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='DELETE')
        
        result = self.open('scene.json', data)
        
        return result



class Note(object):
    """Note calls."""
    def __init__(self, openfunc):
        self.open = openfunc
    
    
    def get(self, proj, annotable_id, note_id):
        """This method is currently unused, but is needed for the 
        RESTController to work.

        Returns:
            ``note``
        """
        data = prep_data(locals(), )
        
        params = encode_params(data)
        result = self.open('note/get_one.json?%s' % params)
        
        return json.loads(result.read())['note']

    
    def new(self, proj, annotable_id, text):
        """Add notes to a ``annotable`` obect.

        Returns:
            ``note``
        """
        data = prep_data(locals(), )
        
        result = self.open('note.json', data)
        
        return json.loads(result.read())['note']

    
    def delete(self, proj, note_id):
        """Delete a note.

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='DELETE')
        
        result = self.open('note.json', data)
        
        return result

    
    def pin(self, proj, note_id):
        """Pin a note.

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='PIN')
        
        result = self.open('note.json', data)
        
        return result

    
    def unpin(self, proj, note_id):
        """Un-pin a note.

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='UNPIN')
        
        result = self.open('note.json', data)
        
        return result



class Tag(object):
    """Tag calls."""
    def __init__(self, openfunc):
        self.open = openfunc
    
    
    def get(self, taggable_id, tag_id):
        """This method is currently unused, but is needed for the 
        RESTController to work.

        Returns:
            ``tag``
        """
        data = prep_data(locals(), )
        
        params = encode_params(data)
        result = self.open('tag/get_one.json?%s' % params)
        
        return json.loads(result.read())['tag']

    
    def new(self, taggable_id, tag_ids=[], new_tags=None):
        """Add tags to a ``taggable`` obect.

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), )
        
        result = self.open('tag.json', data)
        
        return result

    
    def delete(self, tag_id):
        """Delete a tag.

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='DELETE')
        
        result = self.open('tag.json', data)
        
        return result

    
    def remove(self, taggable_id, tag_ids=[]):
        """Remove tags from an object.

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='REMOVE')
        
        result = self.open('tag.json', data)
        
        return result



class Asset(object):
    """Asset calls."""
    def __init__(self, openfunc):
        self.open = openfunc
    
    
    def get(self, proj, asset_id):
        """Return a `standalone` page with the asset history

        Returns:
            ``asset``
        """
        data = prep_data(locals(), )
        
        params = encode_params(data)
        result = self.open('asset/get_one.json?%s' % params)
        
        return json.loads(result.read())['asset']

    
    def new(self, proj, container_type, container_id, category_id, name, comment=None):
        """Create a new asset

        Returns:
            ``asset``
        """
        data = prep_data(locals(), )
        
        result = self.open('asset.json', data)
        
        return json.loads(result.read())##['asset']

    
    def delete(self, proj, asset_id):
        """Delete an asset.
        
        Only delete the asset record from the db, the asset file(s) must be
        removed manually.
        (This should help prevent awful accidents) ;)
        

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='DELETE')
        
        result = self.open('asset.json', data)
        
        return result

    
    def checkout(self, proj, asset_id):
        """Checkout an asset.
        
        The asset will be blocked and only the current owner will be able to
        publish new versions until it is released.
        

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='CHECKOUT')
        
        result = self.open('asset.json', data)
        
        return result

    
    def release(self, proj, asset_id):
        """Release an asset.
        
        The asset will be unblocked and available for other users to checkout.
        

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='RELEASE')
        
        result = self.open('asset.json', data)
        
        return result

    
    def publish(self, proj, asset_id, uploaded, comment=None, uploader=None):
        """Publish a new version of an asset.
        
        This will commit to the repo the file(s) already uploaded in a temporary
        storage area, and create a thumbnail and preview if required.
        

        Returns:
            ``version``
        """
        data = prep_data(locals(), _method='PUBLISH')
        
        result = self.open('asset.json', data)
        
        return json.loads(result.read())##['version']

    
    def submit(self, proj, asset_id, sender, uploaded, receiver, comment=None):
        """Submit an asset to supervisors for approval.

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='SUBMIT')
        
        result = self.open('asset.json', data)
        
        return result

    
    def recall(self, proj, asset_id, comment=None):
        """Recall an asset submitted for approval.

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='RECALL')
        
        result = self.open('asset.json', data)
        
        return result

    
    def sendback(self, proj, asset_id, comment=None):
        """Send back an asset for revision.

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='SENDBACK')
        
        result = self.open('asset.json', data)
        
        return result

    
    def approve(self, proj, asset_id, comment=None):
        """Approve an asset submitted for approval.

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='APPROVE')
        
        result = self.open('asset.json', data)
        
        return result

    
    def revoke(self, proj, asset_id, comment=None):
        """Revoke approval for an asset.

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='REVOKE')
        
        result = self.open('asset.json', data)
        
        return result

    
    def download(self, proj, assetver_id):
        """Return a version of an asset from the repository as a file 
        attachment in the response body.

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), _method='DOWNLOAD')
        
        result = self.open('asset.json', data)
        
        return result



class Client(object):
    """Standalone SPAM client."""
    
    def __init__(self, url):
        self.url = url.rstrip('/')
        
        self.category = Category(self.open)
        self.project = Project(self.open)
        self.shot = Shot(self.open)
        self.libgroup = Libgroup(self.open)
        self.scene = Scene(self.open)
        self.note = Note(self.open)
        self.tag = Tag(self.open)
        self.asset = Asset(self.open)
            
    def login(self, username, password=None):
        """Login in SPAM, and save an access cookie for subsequent commands.
        
        :Parameters:
            username : string
                your username
            password : string
                your password, if no password is given it will be asked at the
                command line
        """
        self.username = username
        if not password:
            password = getpass.getpass()
        credentials = urllib.urlencode(dict(login=username, password=password))
        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj),
                                                        MultipartPostHandler)
        url = '%s/login_handler?__logins=0&came_from=/' % self.url
        self.opener.open(url, credentials)
    
    def open(self, cmd, data=None):
        """Open a SPAM url using the builtin opener.
        
        You should not use "open" directly, use wrapped methods instead.

        :Parameters:
            cmd: string
                Command url without prefix (eg: '/project')
            data: string
                urlencoded POST data
        
        :Returns:
            a file-like object with the http response
        """
        return self.opener.open('%s/%s' % (self.url, cmd.lstrip('/')), data)

    
    def upload(self, uploadfile, uploader=None):
        """
        Upload a file (or a list of files) to a temporary storage area as a
        first step for publishing an asset. The file can then be moved to the
        repository and versioned with the asset controller's "publish" method. 
        
        The path for this storage area can be configured in the .ini file with
        the "upload_dir" variable.
        

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), )
        
        result = self.open('upload', data)
        
        return result

    
    def repo(self, *args):
        """
        Return a file from the repository. We retrive file like that instead of
        serving them statically so we can use authorization (a project file can
        only be requested by a valid project user).

        The path for the projects repository can be configured in the .ini file
        with the "repository" variable.
        

        Returns:
            a file-like response object
        """
        data = prep_data(locals(), )
        
        result = self.open('repo', data)
        
        return result







