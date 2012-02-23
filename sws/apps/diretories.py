import os
import mimetypes

from sws.apps import BaseApplication


class DirectoryListing(BaseApplication):
    def handle_request(self, request, response, addr):
        # Apparently os.path.join will return any component that sounds like an absolute path without doing any joining.
        content_type, _ = mimetypes.guess_type(request.resource)
        if request.resource.startswith("/"):
            resource = request.resource[1:]
        full_path = os.path.join(self.conf['root_dir'], resource)
        
        if not resource and not os.listdir(full_path):
            entity = open(self.conf['index']).read()
        elif os.path.exists(full_path):
            if os.path.isfile(full_path):
                fp = open(full_path)
                entity = fp.read()
                fp.close()
            elif os.path.isdir(full_path):
                index_file = os.path.join(full_path, "index.htm")
                if os.path.isfile(index_file):
                    fp = open(index_file)
                    entity = fp.read()
                    fp.close()
                elif os.path.isfile(index_file + "l"):
                    fp = open(index_file + "l")
                    entity = fp.read()
                    fp.close()
                else:
                    files = []
                    if resource:
                        if resource.endswith("/"):
                            files.append("[d]\t<a href='%s'>%s</a>" % ("..", "(UP)"))
                        else:
                            files.append("[d]\t<a href='%s'>%s</a>" % (".", "(UP)"))
    
                    parent_resource = resource.rsplit("/", 1)[-1]
                    for _file in os.listdir(full_path):
                        prefix = "[d]\t"
                        cur_path = os.path.join(full_path, _file)
                        
                        if os.path.isfile(cur_path):
                            prefix = "[f]\t"
                        
                        file_name = _file if resource.endswith("/") else "/".join([parent_resource, _file])
                        files.append(prefix + "<a href='%s'>%s</a>" % (file_name, _file))
    
                    dir_template = open(self.conf['ls_dir']).read()
                    entity = dir_template.replace("{{directory_name}}", full_path).replace("{{file_listing}}", '<br>'.join(files))
        else:
            entity = open(self.conf['404']).read()
        
        response.headers['Content-length']  = len(entity)
        response.headers['Content-Type']    = content_type
        response.headers['Connection']      = "close"

        response.body = entity
        response.send_response()