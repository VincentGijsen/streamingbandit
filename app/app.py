# -*- coding: utf-8 -*-
# Imports of external stuff
import tornado.escape
import tornado.ioloop
import tornado.web
from tornado.options import define, options
import json,os,yaml
import logging
import logging.handlers

# import Streampy classes
from handlers import corehandlers
from handlers import docshandlers
from handlers import adminhandlers
from handlers import statshandlers
from handlers import managementhandlers

f = open("config.cfg",'r')
settings = yaml.load(f)
f.close()
        
# Logging:
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

access_log = logging.getLogger("tornado.access")
access_log.setLevel(settings["log.level"])
app_log = logging.getLogger("myLogger")
app_log.setLevel(settings["log.level"])

ch = logging.StreamHandler()
ch.setLevel(settings["log.console.level"])
ch.setFormatter(formatter)


logHanderAccess = logging.handlers.RotatingFileHandler(settings["log.access"], maxBytes=4096, backupCount=2)
logHanderApp = logging.handlers.RotatingFileHandler(settings["log.app"], maxBytes=4096, backupCount=2)

logHanderAccess.setFormatter(formatter)
logHanderApp.setFormatter(formatter)

access_log.addHandler(logHanderAccess)
access_log.addHandler(ch)
app_log.addHandler(logHanderApp)
app_log.addHandler(ch)


   
app_log.info("Starting application {0}".format( settings["listen.port"]))


# urls handlers
urls = [

    # static pages (index + API reference)
    (r"/", docshandlers.IndexHandler),
    (r"(?i)/index.html", docshandlers.IndexHandler),
    (r"(?i)/reference.html", docshandlers.ReferenceHandler),
    
    # management interface front-end
    (r"(?i)/management.html", managementhandlers.IndexHandler),
    (r"(?i)/login.html", managementhandlers.LogInHandler),
    (r"(?i)/logout.html", managementhandlers.LogOutHandler),

    # action and reward handler (core)
    (r"(?i)/([0-9]+)/getaction.json", corehandlers.ActionHandler),
    (r"(?i)/([0-9]+)/setreward.json", corehandlers.RewardHandler),
    
    # getting /setting theta (core: but obscure)
    (r"(?i)/([0-9]+)/gettheta.json", corehandlers.ActionHandler),
    (r"(?i)/([0-9]+)/settheta.json", corehandlers.RewardHandler),
     
    # admin / management REST api (REST api for administration of experiments)
    (r"(?i)/admin/exp/add.json", adminhandlers.AddExperiment),
    (r"(?i)/admin/exp/list.json", adminhandlers.GetListOfExperiments),
    (r"(?i)/admin/exp/defaults.json", adminhandlers.ListDefaults),
    (r"(?i)/admin/exp/default/([0-9]+)/get.json", adminhandlers.GetDefault),
    (r"(?i)/admin/exp/([0-9]+)/get.json", adminhandlers.GetExperiment),
    (r"(?i)/admin/exp/([0-9]+)/delete.json", adminhandlers.DeleteExperiment),
    (r"(?i)/admin/exp/([0-9]+)/edit.json", adminhandlers.EditExperiment),

    # analytics REST api (REST api for stats / logs)
    (r"(?i)/stats/([0-9]+)/getcurrenttheta.json", statshandlers.WorkInProgress),
    (r"(?i)/stats/([0-9]+)/gethourlytheta.json", statshandlers.WorkInProgress),
               
            
]

tornadoConfig = dict({
    "template_path": os.path.join(os.path.dirname(__file__),"templates"),
    "static_path": os.path.join(os.path.dirname(__file__),"static"),
    "debug": True,   # Should get from config?
    "cookie_secret":"12"
})

application = tornado.web.Application(urls,**tornadoConfig)

def main():
    application.listen(settings["listen.port"])
    tornado.ioloop.IOLoop.instance().start()

# Starting Server:
if __name__ == "__main__":
    main()

# This one works:
# http://localhost:8080/1/getAction.json?context={}&key=12321
# http://localhost:8080/1/setReward.json?key=12321&reward=1&action={}
