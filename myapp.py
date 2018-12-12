import cgi
import os
import subprocess
import traceback

import portpicker
import wsgi_proxy


def terminate_process(name):
    if os.name == 'nt':
        subprocess.call(['taskkill', '/f', '/im', str(name)])
    elif os.name == 'posix':
        subprocess.call(['killall', '-9', str(name)])


class WSGIHandler(object):
    server_program_path = None
    server_program_port = None
    server_program_process = None
    upload_password = None
    upload_query = None

    def __init__(self):
        if os.name == 'nt':
            self.server_program_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'USERRES/server.exe')
        elif os.name == 'posix':
            self.server_program_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'USERRES/server')
        self.upload_password = os.environ.get('BKAPP_UPLOAD_PASSWORD')
        self.upload_query = os.environ.get('BKAPP_UPLOAD_QUERY')

    def run_server_program(self):
        self.server_program_port = portpicker.pick_unused_port()
        os.chmod(self.server_program_path, 0o755)
        try:
            self.server_program_process = subprocess.Popen([self.server_program_path, str(self.server_program_port)], close_fds=True)
        except:
            traceback.print_exc()
            self.server_program_process = None
        return self.server_program_process

    def teminate_server_process(self):
        name = os.path.basename(self.server_program_path)
        try:
            terminate_process(name)
        except:
            traceback.print_exc()

    def handle_upload_get(self, environ, start_response):
        if not self.upload_password:
            content = u'Upload is not allowed.'
            content = content.encode()
            start_response('403 Forbidden', [
                ('Content-Type', 'text/plain; charset=UTF-8'),
                ('Content-Length', str(len(content))),
            ])
            return [content]

        content = u'''
<form method="post" enctype="multipart/form-data">
    <p><input type="password" name="password"></p>
    <p><input type="file" name="file"></p>
    <p><button type="submit">Upload</button></p>
</form>
'''
        content = content.encode()
        start_response('200 OK', [
            ('Content-Type', 'text/html; charset=UTF-8'),
            ('Content-Length', str(len(content))),
        ])
        return [content]

    def handle_upload_post(self, environ, start_response):
        if not self.upload_password:
            content = u'Upload is not allowed.'
            content = content.encode()
            start_response('403 Forbidden', [
                ('Content-Type', 'text/plain; charset=UTF-8'),
                ('Content-Length', str(len(content))),
            ])
            return [content]

        try:
            fields = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        except Exception as e:
            traceback.print_exc()
            content = e.message
            content = content.encode()
            start_response('400 Bad Request', [
                ('Content-Type', 'text/plain; charset=UTF-8'),
                ('Content-Length', str(len(content))),
            ])
            return [content]

        if 'password' not in fields or fields['password'].value != self.upload_password:
            content = u'Password is empty or password wrong!'
            content = content.encode()
            start_response('401 Unauthorized', [
                ('Content-Type', 'text/plain; charset=UTF-8'),
                ('Content-Length', str(len(content))),
            ])
            return [content]

        if 'file' not in fields or not isinstance(fields['file'], cgi.FieldStorage):
            content = u'Field "file" not exists or is not a file or contains multiple files.'
            content = content.encode()
            start_response('400 Bad Request', [
                ('Content-Type', 'text/plain; charset=UTF-8'),
                ('Content-Length', str(len(content))),
            ])
            return [content]

        self.teminate_server_process()

        file_item = fields['file']
        file_item.file.seek(0, os.SEEK_END)
        file_len = file_item.file.tell()
        file_item.file.seek(0)
        if file_len > 0:
            path = self.server_program_path
            path_dir = os.path.dirname(path)
            if not os.path.exists(path_dir):
                os.makedirs(path_dir, mode=0o755)
            with open(path, 'wb') as f:
                f.write(file_item.file.read())

        self.run_server_program()

        content = u'The file was uploaded successfully.'
        content += u'\n'
        content += u'Server runs at pid {} listening on port {}.'.format(self.server_program_process.pid, self.server_program_port)
        content = content.encode()
        start_response('200 OK', [
            ('Content-Type', 'text/plain; charset=UTF-8'),
            ('Content-Length', str(len(content))),
        ])
        return [content]

    def __call__(self, environ, start_response):
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']
        query = environ['QUERY_STRING']

        if method == 'GET' and path == '/upload' and query == self.upload_query:
            return self.handle_upload_get(environ, start_response)
        if method == 'POST' and path == '/upload' and query == self.upload_query:
            return self.handle_upload_post(environ, start_response)

        environ['HTTP_HOST'] = '127.0.0.1:' + str(self.server_program_port)
        environ['wsgi.url_scheme'] = 'http'
        return wsgi_proxy.app(environ, start_response)
