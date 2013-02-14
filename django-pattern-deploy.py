#!/usr/bin/python
import subprocess
import os
import sys
import shutil
import stat
from optparse import OptionParser

TEMPLATE_PROJECT_PATH="https://github.com/lexich/django-pattern/zipball/master"

class FileNotFoundException(Exception):
    """docstring for FileNotFoundException"""
    pass

class ToolNotFoundExeption(Exception):
    """docstring for ToolNotFoundExeption"""
    pass
        

def rm_rf(top):
    """Recursive remove folder from top"""
    if not os.path.exists(top):
        return
    print "Clear project"
    def remove_readonly(fn, path, excinfo):
        """Help function to rmtree function of shutil module"""
        if fn is os.rmdir:
            os.chmod(path, stat.S_IWRITE)
            os.rmdir(path)
        elif fn is os.remove:
            os.chmod(path, stat.S_IWRITE)
            os.remove(path)
    return shutil.rmtree(top, onerror=remove_readonly)


def exec_system(params, cwd=None):
    """wrapper to subprocess.call func"""
    print( "\nRun:\t{0}".format(" ".join(params)) )
    #p = subprocess.Popen(params,cwd=cwd, shell=True)
    #p.wait()
    #os.system( " ".join(params) )
    print params
    subprocess.check_call(params, cwd=cwd)
    print("OK")
    

def is_win():
    return sys.platform == "win32"

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

def virtualenv(cwd, debug=False):
    virtualenv = which("virtualenv")    
    packages = '--no-site-packages' \
        if not debug else '--system-site-packages'
    env = os.path.join(cwd, ".env" )
    exec_system([
       virtualenv,
       packages,
       env
    ])
    env_bin = os.path.join(env,"Scripts") \
        if sys.platform == 'win32' else os.path.join(env,"bin")
    activate_this = os.path.join(env_bin,"activate_this.py")
    execfile(activate_this, dict(__file__=activate_this))

def startproject(projectname, template_project_path, debug):
    """
    wrapper to django-admin startproject $projectname
    raise FileNotFoundException
    return python path executor
    """    
    python = ""
    pip = ""    
    try:        
        virtualenv(projectname, debug)        
        python = which('python')
        pip = which('pip')
    except ToolNotFoundExeption, e:
        print e
    
    exec_system([
        pip,'install','django'
    ])
    django_admin = find_path('django-admin.py')
    exec_system([
      python, 
      django_admin,
      'startproject', 
      projectname, 
     '--template={0}'.format(template_project_path)
    ], cwd=projectname)
    
    exec_system([
       pip,'install','-r',
       os.path.join(projectname, projectname, 'requirements.txt')
    ])
    return os.path.join(projectname,projectname)


class Manage(object):
    """docstring for Manage 
        wrapper to manage.py
    """
    def __init__(self, cwd):
        self.cwd = cwd
        self.python = which('python')
        self.manage = 'manage.py'
        if not os.path.exists(os.path.join(self.cwd,self.manage) ):
            raise FileNotFoundException("File %s not found" % self.manage )

    def _m(self, *args):
        params = [self.python, self.manage] \
            + [ x for x in args ]        
        exec_system( params, cwd=self.cwd )

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
        
class Node(object):
    def __init__(self, cwd):
        self.cwd = cwd

    def _exec(self, params):
        exec_system( params, cwd=self.cwd)

    def npm_install(self):        
        npm = which("npm")
        self._exec([npm,'install'])        

    def ext(self):
        return ".cmd" if is_win() else ""    

    def bower_install(self):                
        bower = os.path.join("node_modules",".bin","bower%s" % self.ext() )
        self._exec([bower, 'install'])

    def grunt(self):
        grunt = os.path.join("node_modules",".bin","grunt%s" % self.ext() )
        self._exec([grunt])


def main(projectname, template, debug):
    if not which("python"): return    
    rm_rf(
        os.path.join(projectname,projectname)
        #projectname        
    )
    try:
        path = startproject(
            projectname, 
            template,
            debug
        )        
        manage = Manage(path)
        manage.syncdb()
        manage.migrate()
        manage.createsuperuser()
        node = Node(path)
        node.npm_install()
        node.bower_install()
        node.grunt()
        manage.collectstatic()
        manage.runserver()        
    except FileNotFoundException, e:
        print e    
    except ToolNotFoundExeption, e:
        print e
    except Exception, e:    
        print e

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-n", "--name", dest="projectname",
        help="name of django project")
    parser.add_option("-t", "--template", dest="template", 
        default=TEMPLATE_PROJECT_PATH,
        help="template for django project (django-admin.py startproject --template=TEMPLATE")
    parser.add_option("-d", "--debug",
          action="store_true", dest="debug", default=False,
          help="debug mode")
    (opt, args) = parser.parse_args()
    if opt.projectname:
        main(opt.projectname, opt.template, opt.debug)
