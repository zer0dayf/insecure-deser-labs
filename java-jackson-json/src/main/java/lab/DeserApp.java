package lab;

import com.fasterxml.jackson.annotation.JsonTypeInfo;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class DeserApp {
    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        // Intentionally unsafe polymorphic deserialization, for localhost lab only.
        mapper.enableDefaultTyping(ObjectMapper.DefaultTyping.NON_FINAL, JsonTypeInfo.As.PROPERTY);
        // Read the COMPLETE request body, including multiline JSON from Burp Repeater.
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in, "UTF-8"));
        StringBuilder body = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) body.append(line).append('\n');
        String json = body.toString();
        if (json.trim().isEmpty()) return;
        System.out.println("[input] Jackson JSON deserialization");
        Object result = mapper.readValue(json, Object.class);
        if (result instanceof java.util.Map) {
            Object message = ((java.util.Map<?, ?>) result).get("message");
            if (message != null) System.out.println("[response] " + message);
        }
        System.out.println("[result] Type: " + (result == null ? "null" : result.getClass().getName()));
        System.out.println("[result] Value: " + String.valueOf(result));
    }
}
