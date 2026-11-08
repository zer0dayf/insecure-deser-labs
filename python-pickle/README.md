# Python pickle (8084)

The target application has **no custom gadget class**. `pickle.loads()` implements Python's built-in `REDUCE` opcode and can invoke a callable specified in the serialized stream. The generator's `__reduce__` is *only used locally to construct the malicious serialized bytes*; that class is not present or needed on the target. See `../payloads.md`.
