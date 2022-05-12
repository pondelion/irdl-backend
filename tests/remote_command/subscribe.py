import time

from irdl.services.remote_command import CentralServerMessageHandler


csmh = CentralServerMessageHandler()
csmh2 = CentralServerMessageHandler()
print(csmh)
print(csmh2)
csmh.subscribe()

try:
    while True:
        time.sleep(0.2)
except KeyboardInterrupt:
    pass
