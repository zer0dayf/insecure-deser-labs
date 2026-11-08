import base64
import pickle

print("LOCAL LAB - paste one Base64 pickle payload:")
b64 = input().strip()
data = base64.b64decode(b64, validate=True)
# VULNERABLE SINK: pickle can invoke arbitrary callables during reconstruction.
value = pickle.loads(data)
print("Deserialized type:", type(value).__name__)
print("Deserialized value:", repr(value))
