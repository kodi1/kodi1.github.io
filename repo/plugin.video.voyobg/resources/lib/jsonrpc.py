import json
import urllib
import base64
import requests
from kodibgcommon.utils import log

class JsonRpc(dict):
  def __init__(self, id=0):
    self.jsonrpc = "2.0"
    if id != 0:
      self.id = id
  
  def __getattr__(self, key):
    self.method = key
    def __call_method__( args ):
      self.params = args
      return json.dumps(self.__dict__)
    return __call_method__

class JsonBatch():
  
  def __init__(self):
    self.response = None
    self.calls = []
    rpc = JsonRpc()
    self.calls.append(rpc.notifyKey([base64.b64decode("dm95b2RhYmVzdGluZGFmb3Jlc3Q=")]))
    rpc = JsonRpc()
    self.calls.append(rpc.notifyVersion(["ANDROID"]))
  
  def append(self, rpc):
    self.calls.append(rpc)

  def get_encoded_calls(self):
    log(",".join(self.calls))
    __calls__ = ",".join(self.calls)
    __calls__ = "[%s]" % __calls__.replace(', ', ',').replace(': ', ':')
    return urllib.quote_plus(__calls__)
    
  def execute(self):
    url = base64.b64decode("aHR0cDovL3ZveW8uYmcvYmluL2VzaG9wL3dzL2FwaS9qc29uLnBocD9qc29ucnBjPSVz") % self.get_encoded_calls()
    log(url)
    try:
      r = requests.get(url)
      self.response = r.json()
      return self.response
    except:
      log("Error during execute()", 4)
      return []
      
  def get_result_by_id(self, id):
    for res in self.response:
      if res.get("id") and res["id"] == str(id):
        return res["result"]
    return None