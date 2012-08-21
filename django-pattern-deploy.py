import subprocess
import os
import sys
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

def find_tool(name, path):          
    path.append(name)
    tool = os.path.join(*path)
    if os.path.isfile(tool):
        return tool
    return which(name)


def startproject(projectname, template_project_path):
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
        '--template={0}'.format(template_project_path)
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

    env_bin = os.path.join(env,"Scripts") if sys.platform == 'win32' else os.path.join(env,"bin")
    activate_this = os.path.join(env_bin,"activate_this.py")
    execfile(activate_this, dict(__file__=activate_this))    
    pip = which('pip')
    python = which('python')
    system([
       pip,'install','-r',
       os.path.join(projectname,'requirements.txt')
    ])


class Manage(object):
    """docstring for Manage 
        wrapper to manage.py
    """
    def __init__(self, projectname):
        self.python = which('python')
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
        

def main(projectname, template_project_path):
    if not which("python"): return
    print "Clear project"
    rm_rf(projectname)
    try:
        startproject(
            projectname, 
            template_project_path
        )        
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
    except ToolNotFoundExeption, e:
        print e

if __name__ == '__main__':
    if len(os.sys.argv) > 1:
        projectname = os.sys.argv[1]
        template = TEMPLATE_PROJECT_PATH
        if len(os.sys.argv) > 2:
            template = os.sys.argv[2]
        main(projectname, template)
