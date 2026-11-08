# .NET BinaryFormatter — port 8082

Start: `docker compose up --build -d dotnet`. Visit http://127.0.0.1:8082 and paste one-line **Base64** representing a BinaryFormatter stream.

## Generate a candidate with ysoserial.net

On a Windows workstation where you've downloaded and built `ysoserial.net` (not included in this ZIP):

```powershell
.\ysoserial.exe -g TypeConfuseDelegateMono -f BinaryFormatter -c "id" -o base64
```

Copy just the Base64 output into the browser. `-c` sets a command that would be run **inside the target** if the selected gadget works. The chosen command `id` is a Linux proof command, not Windows Calculator.

## What to expect

`Program.cs` calls `BinaryFormatter.Deserialize()` without an allowlist. The Docker target is Mono 6.12 on Linux. `ysoserial.net` gadget chains are implementation/runtime dependent; a chain that runs on Windows .NET Framework **may fail on Mono**, even if the payload is correctly encoded. If the target throws a deserialization exception, inspect the error but do not infer working OS execution. The Mono-specific generator is a better candidate than the Windows .NET Framework variant, but it is **not verified** on this exact container image.

```powershell
docker compose logs --tail=100 dotnet
```

For Windows .NET Framework gadget compatibility testing, use a disposable Windows VM rather than treating Mono as equivalent.


For normal vs gadget payloads and comparison, see [../payloads.md](../payloads.md).
