package lab;

/** Intermediate gadget; no shell command is hard-coded here. */
public class TaskRouter {
    private ProcessAction action;
    public TaskRouter() {}
    public void setAction(ProcessAction action) {
        System.out.println("[2] TaskRouter.setAction() called");
        this.action = action;
    }
    public ProcessAction getAction() { return action; }
    public void dispatch() throws Exception {
        System.out.println("[3] TaskRouter.dispatch() called");
        if (action != null) action.execute();
    }
    @Override public String toString() { return "TaskRouter{action=" + action + "}"; }
}
