# --------------------------------------------------------------------------- # 
# import the various server implementations
# --------------------------------------------------------------------------- # 
from pymodbus.version import version
from pymodbus.server.sync import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
# --------------------------------------------------------------------------- # 
# import the payload builder
# --------------------------------------------------------------------------- # 
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
# --------------------------------------------------------------------------- # 
# configure the service logging
# --------------------------------------------------------------------------- # 
import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT,filename='mbserv.log')
log = logging.getLogger()
log.setLevel(logging.DEBUG)
# --------------------------------------------------------------------------- # 
# configure the service logging
# --------------------------------------------------------------------------- # 
from pymodbus.client.sync import ModbusTcpClient


import sys
import os
import threading
import ctypes
   
class Mbserv(threading.Thread):
    def __init__(self,ip,inter,port,nreg):
        threading.Thread.__init__(self)
        self.ip = ip
        self.inter = inter
        self.port = int(port)
        self.nreg = int(nreg)
        self.running = False

    def run(self)-> bool:
        try:
            
            #cmd = "sudo ip addr add " + self.ip +"/24 dev " + self.inter
            #logging.debug("%s",cmd)
            #os.system(cmd)
            
            self.running = True
            logging.debug("Demarrage du thread à l'adresse %s",self.ip)
            self.mb_server()

        except:
            self.running = False
            logging.debug("echec thread à l'adresse %s",self.ip)
            raise Exception("echec " + self.ip)

    def get_id(self):
 
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')
            
    def mb_server(self):
        add = (self.ip,self.port)
        
        builder = BinaryPayloadBuilder(byteorder=Endian.Little,
                                   wordorder=Endian.Little)
        for i in range(self.nreg):
            builder.add_16bit_uint(0xFFFF)
 
        # ----------------------------------------------------------------------- #
        # use that payload in the data store
        # ----------------------------------------------------------------------- #
        # Here we use the same reference block for each underlying store.
        # ----------------------------------------------------------------------- #
    
        block = ModbusSequentialDataBlock(1, builder.to_registers())
        store = ModbusSlaveContext(di=block, co=block, hr=block, ir=block)
        context = ModbusServerContext(slaves=store, single=True)
    
        # ----------------------------------------------------------------------- #
        # initialize the server information
        # ----------------------------------------------------------------------- #
        # If you don't set this or any fields, they are defaulted to empty strings.
        # ----------------------------------------------------------------------- #
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'Pymodbus'
        identity.ProductCode = 'PM'
        identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
        identity.ProductName = 'Pymodbus Server'
        identity.ModelName = 'Pymodbus Server'
        identity.MajorMinorRevision = version.short()
        # ----------------------------------------------------------------------- #
        # run the server you want
        # ----------------------------------------------------------------------- #
        StartTcpServer(context, identity=identity, address=add)
    
    def alive(self):
        try:
            client = ModbusTcpClient(self.ip,self.port)
            assert client.connect()
            self.running =True
            return True
        except:
            self.running =False
            return False



