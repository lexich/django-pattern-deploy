import subprocess
import os
import shutil
import stat

TEMPLATE_PROJECT_PATH="https://github.com/lexich/django-pattern/zipball/master"

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
    for path in os.environ['PATH'].split(os.pathsep):
        file_path = os.path.join(path,filename)
        if os.path.exists(file_path):
            return file_path
    raise FileNotFoundException('File %s not found' % filename )


def find_tool(name, paths):
    for path in paths:
	print path
	path.append(name)
	tool = os.path.join(*path)
    	if os.path.exists(tool):
            print("find_tool %s" % tool)
            return tool
    return name

	
def startproject(projectname):
    """
    wrapper to django-admin startproject $projectname
    raise FileNotFoundException
    """
    django_admin = find_path('django-admin.py')
    python = 'python'
    subprocess.call([
        python, 
        django_admin, 
        'startproject', 
        projectname, 
        '--template={0}'.format(TEMPLATE_PROJECT_PATH)
        ])  
    print "Create projectname"
    env = os.path.join(projectname,'.env')
    subprocess.call([
	"virtualenv",
	os.path.join(projectname,'.env')
    ])
    tool_path = [[env,"bin"],[env,"Script"]]
    pip = find_tool("pip", tool_path)
    python = find_tool("python", tool_path)
    subprocess.call([
	pip,'install','-r',
	os.path.join(projectname,'requirements.txt')
    ])
    return python



class Manage(object):
    """docstring for Manage 
        wrapper to manage.py
    """
    def __init__(self, projectname,python='python'):
        self.python = python
        self.manage = os.path.join('.',projectname,'manage.py')
        if not os.path.exists(self.manage):
            raise FileNotFoundException("File %s not found" % self.manage )

    def _m(self, *args):
        params = [self.python, self.manage ] 
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
        """ index management command"""
        self._m('autocreatesuperuser')

    def collectstatic(self):
        self._m("collectstatic","--noinput")
        

def main(projectname):
    print "Clear project"
    rm_rf(projectname)
    try:
        python = startproject(projectname)
        print( "Python path %s" % python)
        manage = Manage(projectname, python)        
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
