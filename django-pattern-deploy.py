import subprocess
import os
import shutil
import stat

TEMPLATE_PROJECT_PATH="https://github.com/lexich/django-pattern/zipball/master"

class FileNotFoundException(Exception):
    """docstring for FileNotFoundException"""
    pass

class ToolNotFoundExeption(Exception):
    """docstring for ToolNotFoundExeption"""
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


def system(params):
    """wrapper to subprocess.call func"""
    print( "\nRun:\t{0}".format(" ".join(params)) )
    result = "OK" if subprocess.call(params) == 0 else "FAIL"
    print( "Resuls:\t{0}\n".format(result) )


def find_path(filename):
    """find filepath of filename in System PATH"""
    for path in os.environ['PATH'].split(os.pathsep):
        file_path = os.path.join(path,filename)
        if os.path.exists(file_path):
            return file_path
    raise FileNotFoundException('File %s not found' % filename )


def which(program):
    """
    check executable program
    http://stackoverflow.com/a/377028/1513126
    """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    if program.endswith(".exe"):
        raise ToolNotFoundExeption("Tool not found: '%s'" % program)
    else:
        return which("%s.exe" % program)

def find_tool(name, paths):
    for path in paths:        
        path.append(name)
        tool = os.path.join(*path)
        if os.path.isfile(tool):
            return tool
    return which(name)


def startproject(projectname):
    """
    wrapper to django-admin startproject $projectname
    raise FileNotFoundException
    return python path executor
    """
    django_admin = find_path('django-admin.py')    
    env = os.path.join(projectname,'.env')
    python = which('python')

    system([
        python, 
        django_admin, 
        'startproject', 
        projectname, 
        '--template={0}'.format(TEMPLATE_PROJECT_PATH)
    ])
    try:
        virtualenv = which("virtualenv")
        system([
           virtualenv,
           '--no-site-packages',
           os.path.join(projectname,'.env')
        ])
    except ToolNotFoundExeption, e:
        print e
    
    tool_path = [[env,"bin"],[env,"Scripts"]]
    pip = find_tool("pip", tool_path)
    python = find_tool("python", tool_path)
    system([
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
        system( params )

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
    if not which("python"): return
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
    except ToolNotFoundExeption, e:
        print e

if __name__ == '__main__':
    if len(os.sys.argv) > 1:
        main(os.sys.argv[1])
