import subprocess
import os
import shutil
import stat

TEMPLATE_PROJECT_PATH="https://github.com/lexich/django-pattern/master"

class FileNotFoundException(Exception):
    """docstring for FileNotFoundException"""
    pass


def rm_rf(top):
    if not os.path.exists(top):
        return
    """Recursive remove folder from top"""
    def remove_readonly(fn, path, excinfo):
        """Help function to rmtree function of shutil module"""
        if fn is os.rmdir:
            os.chmod(path, stat.S_IWRITE)
            os.rmdir(path)
        elif fn is os.remove:
            os.chmod(path, stat.S_IWRITE)
            os.remove(path)
    return shutil.rmtree(top, onerror=remove_readonly)



def find_path(filename):
    """find filepath of filename in System PATH"""
    for path in os.environ['path'].split(';'):
        file_path = os.path.join(path,filename)
        if os.path.exists(file_path):
            return file_path
    raise FileNotFoundException('File %s not found' % filename )

def startproject(projectname):
    """
    wrapper to django-admin startproject $projectname
    raise FileNotFoundException
    """
    django_admin = find_path('django-admin.py')
    subprocess.call([
        'python', 
        django_admin, 
        'startproject', 
        projectname, 
        '--template={0}'.format(TEMPLATE_PROJECT_PATH)
        ])  
    print "Create projectname"



class Manage(object):
    """docstring for Manage 
        wrapper to manage.py
    """
    def __init__(self, projectname):
        self.manage = os.path.join('.',projectname,'manage.py')
        if not os.path.exists(self.manage):
            raise FileNotFoundException("File %s not found" % self.manage )

    def _m(self, *args):
        params = ['python', self.manage ] 
        for arg in args:
            params.append(arg)
        subprocess.call( params )

    def runserver(self, port='8000'):
        """wrapper manage.py runserver"""
        self._m('runserver', port)

    def syncdb(self):
        self._m('syncdb', '--noinput')

    def migrate(self):
        self._m('migrate')  

    def createsuperuser(self):
        self._m('createsuperuser',
            '--username=admin',
            '--email=admin@admin.com',
            '--noinput'
        )

    def collectstatic(self):
        self._m("collectstatic","--noinput")
        

def main(projectname):
    print "Clear project"
    rm_rf(projectname)
    try:
        startproject(projectname)
        manage = Manage(projectname)        
        manage.syncdb()
        manage.migrate()
        manage.createsuperuser()
        manage.collectstatic()
        manage.runserver()
    except FileNotFoundException, e:
        print e
    except Exception, e:
        print e

if __name__ == '__main__':
    if len(os.sys.argv) > 1:
        main(os.sys.argv[1])