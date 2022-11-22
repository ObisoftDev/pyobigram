import threading
from .utils import createID

class StoppableThread(threading.Thread):
    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class ObigramThread(object):
    def __init__(self,targetfunc=None,args=(),update=None):
        self.id = createID(12)
        self.handle = threading.Thread(target=targetfunc, args=args)
        self.update = update
        self.tstore = {}
        pass
    def start(self):
        self.handle.start()
    def stop(self):
        self.handle.join()
        pass
    def store(self,name,obj):
        self.tstore[name] = obj
    def getStore(self,name):
        try:
            return self.tstore[name]
        except:pass
        return None