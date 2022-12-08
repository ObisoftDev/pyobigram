import os
from io import BufferedReader
import time

import requests
from .utils import get_file_size,get_url_file_name,req_file_size

class MonitorReader(object):
    def __init__(self,total=100):
        self.chunk_por = 0
        self.chunkrandom = 100
        self.total = total
        self.time_start = time.time()
        self.time_total = 0
        self.size_per_second = 0
        self.clock_start = time.time()
    def can_step(self,size=0):
        self.chunk_por += size
        self.size_per_second += size
        tcurrent = time.time() - self.time_start
        self.time_total += tcurrent
        self.time_start = time.time()
        if self.time_total>=1:
            self.clock_time = (self.total - self.chunk_por) / (self.size_per_second)
            return True
        return False
    def cleanup(self):
        self.time_total = 0
        self.size_per_second = 0

class FileProgressReader(BufferedReader):
    def __init__(self,filepath='',read_size=1024,progress_func=None,progress_args=None,self_in = None,normalize=False):
        self.file_path = filepath
        self.file_name = str(self.file_path).split('/')[-1]
        self.file = open(filepath,'rb')
        self.read_size = read_size
        self.progress_func = progress_func
        self.progress_args = progress_args
        self.file_size = get_file_size(self.file_path)
        self.chunk_por = 0
        self.chunkrandom = 100
        self.time_start = time.time()
        self.time_total = 0
        self.size_per_second = 0
        self.clock_start = time.time()
        self.self_in = self_in
        self.normalize = normalize
        BufferedReader.__init__(self,self.file,self.read_size)

    def __len__(self):
        return self.file_size

    def read(self, size=1024):
        if self.normalize:
            chunk = self.file.read(size)
        else:
            chunk = self.file.read(self.read_size)
        try:
            self.chunk_por += len(chunk)
            self.size_per_second+=len(chunk)
            tcurrent = time.time() - self.time_start
            self.time_total += tcurrent
            self.time_start = time.time()
            if self.time_total>=1:
               self.clock_time = (self.file_size - self.chunk_por) / (self.size_per_second)
               if self.progress_func:
                  self.progress_func(self.self_in,self.file_name,self.chunk_por,self.file_size,self.size_per_second,self.clock_time,self.progress_args)
               self.time_total = 0
               self.size_per_second = 0
        except:pass
        return chunk

    def flush(self,data=None):
        self.file.flush()

    def close(self):
        try:
            if self.progress_func:
                  self.progress_func(self.self_in,self.file_name,self.file_size,self.file_size,self.self.file_size,self.clock_time,self.progress_args)
        except:pass
        self.file.close()

class FileUrlProgressReader(BufferedReader):
    def __init__(self,url='',read_size=1024,progress_func=None,progress_args=None,self_in = None):
        self.url = url
        self.chunk_por = 0
        self.req = self.make_get()
        self.file_name = get_url_file_name(self.url,self.req)
        self.read_size = read_size
        self.progress_func = progress_func
        self.progress_args = progress_args
        self.file_size = req_file_size(self.req)
        self.chunkrandom = 100
        self.time_start = time.time()
        self.time_total = 0
        self.size_per_second = 0
        self.clock_start = time.time()
        self.self_in = self_in
        temp = open('temp.url','w')
        temp.write(f'{self.url}')
        temp.close()
        self.file = open('temp.url','rb')
        BufferedReader.__init__(self,self.file,self.read_size)

    def make_get(self,read=False):
        resp = None
        if not read:
            resp = requests.get(self.url,stream = True,allow_redirects=True)
        else:
            headers = {}
            headers['Range'] = f'bytes={self.chunk_por}-{self.read_size}'
            resp = requests.get(self.url,stream = True,allow_redirects=True,headers=headers)
        return resp

    def __len__(self):
        return self.file_size

    def read(self, size=1024):
        chunk = b''
        resp = self.make_get(True)
        chunk += resp.content
        self.chunk_por += len(chunk)
        self.size_per_second+=len(chunk)
        tcurrent = time.time() - self.time_start
        self.time_total += tcurrent
        self.time_start = time.time()
        if self.time_total>=1:
           self.clock_time = (self.file_size - self.chunk_por) / (self.size_per_second)
           if self.progress_func:
              self.progress_func(self.self_in,self.file_name,self.chunk_por,self.file_size,self.size_per_second,self.clock_time,self.progress_args)
           self.time_total = 0
           self.size_per_second = 0
        return chunk

    def flush(self,data=None):
        self.file.flush()

    def close(self):
        try:
            if self.progress_func:
                  self.progress_func(self.self_in,self.file_name,self.file_size,self.file_size,self.self.file_size,self.clock_time,self.progress_args)
            os.unlink('temp.url')
        except:pass
        self.file.close()

#file = FileUrlProgressReader(url='https://www.7-zip.org/a/7z2201-x64.exe')
#chunk = file.read()
#print('')
