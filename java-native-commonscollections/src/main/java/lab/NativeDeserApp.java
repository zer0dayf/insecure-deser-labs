package lab;

import java.io.ByteArrayInputStream;
import java.io.ObjectInputStream;
import java.util.Base64;
import java.util.Scanner;
import java.io.ByteArrayOutputStream;
import java.io.ObjectOutputStream;
import java.util.ArrayList;

/** Intentionally unsafe: runs only inside a disposable, loopback-published lab. */
public class NativeDeserApp {
    public static void main(String[] args) throws Exception {
        if (args.length > 0 && "--generate-benign".equals(args[0])) {
            ArrayList<String> item = new ArrayList<>();
            item.add("hello-from-java");
            ByteArrayOutputStream buffer = new ByteArrayOutputStream();
            try (ObjectOutputStream out = new ObjectOutputStream(buffer)) { out.writeObject(item); }
            System.out.println(Base64.getEncoder().encodeToString(buffer.toByteArray()));
            return;
        }
        System.out.println("Paste Base64-encoded Java serialization stream (AC ED 00 05):");
        Scanner scanner = new Scanner(System.in, "UTF-8");
        if (!scanner.hasNextLine()) return;
        String input = scanner.nextLine().trim();
        byte[] serialized = Base64.getDecoder().decode(input);

        // No ObjectInputFilter, class allowlist, or custom validation by design.
        // A suitable classpath gadget can execute code *during* readObject().
        try (ObjectInputStream stream = new ObjectInputStream(new ByteArrayInputStream(serialized))) {
            Object result = stream.readObject(); // VULNERABLE SINK
            System.out.println("Deserialized type: " + (result == null ? "null" : result.getClass().getName()));
            System.out.println("Deserialized value: " + result);
        }
    }
}
