using System;
using System.IO;
using System.Runtime.Serialization.Formatters.Binary;

class Program
{
    static void Main(string[] args)
    {
        if (args.Length > 0 && args[0] == "--generate-benign")
        {
#pragma warning disable SYSLIB0011
            using (var outstream = new MemoryStream())
            {
                new BinaryFormatter().Serialize(outstream, "hello-from-dotnet");
                Console.WriteLine(Convert.ToBase64String(outstream.ToArray()));
            }
#pragma warning restore SYSLIB0011
            return;
        }
        Console.WriteLine("LOCAL LAB - paste one Base64 BinaryFormatter payload:");
        string line = Console.ReadLine();
        byte[] data = Convert.FromBase64String(line ?? "");
        // VULNERABLE SINK. Use ONLY inside an isolated disposable Windows VM.
#pragma warning disable SYSLIB0011
        BinaryFormatter formatter = new BinaryFormatter();
        using (MemoryStream stream = new MemoryStream(data))
        {
            object obj = formatter.Deserialize(stream);
            Console.WriteLine("Deserialized type: " + obj.GetType().FullName);
            Console.WriteLine("Deserialized value: " + obj);
        }
#pragma warning restore SYSLIB0011
    }
}
