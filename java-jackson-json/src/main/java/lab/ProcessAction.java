package lab;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.concurrent.TimeUnit;

/** Deliberately dangerous OS execution sink for an isolated training container. */
public class ProcessAction {
    private String command;
    public ProcessAction() {}
    public void setCommand(String command) {
        System.out.println("[4] ProcessAction.setCommand() called");
        this.command = command;
    }
    public String getCommand() { return command; }
    public void execute() throws Exception {
        System.out.println("[5] ProcessAction.execute() => OS process launch");
        if (command == null || command.trim().isEmpty()) throw new IllegalArgumentException("Missing command");
        Process process = new ProcessBuilder("/bin/sh", "-c", command).redirectErrorStream(true).start();
        // Wait for a short finite duration, then collect observed output.
        if (!process.waitFor(3, TimeUnit.SECONDS)) {
            process.destroyForcibly();
            throw new IllegalStateException("OS process timed out");
        }
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), "UTF-8"));
        String line;
        while ((line = reader.readLine()) != null) System.out.println("[os stdout] " + line);
        System.out.println("[os exit] " + process.exitValue());
    }
    @Override public String toString() { return "ProcessAction{command=" + command + "}"; }
}
