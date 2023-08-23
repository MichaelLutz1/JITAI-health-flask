import sys

sys.path.insert(0, "/usa/kumar/JITAI/JITAICoach/")
activate_this = '/usa/kumar/python-environments/besmart_env4/bin/activate_this.py'

with open(activate_this, "r") as f:
        exec(f.read(), {'__file__': activate_this})

#with open(activate_this, "r") as f:
        #code = compile(f.read(), activate_this, 'exec')
        #exec(code, globals(), locals())

from JITAI_server import app as application
