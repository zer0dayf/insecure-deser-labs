package lab;

/** Demonstration-only gadget entry: setter side effects during Jackson binding. */
public class WorkflowEnvelope {
    private TaskRouter router;
    public WorkflowEnvelope() {}
    public void setRouter(TaskRouter router) throws Exception {
        System.out.println("[1] WorkflowEnvelope.setRouter() invoked by Jackson");
        this.router = router;
        if (router != null) router.dispatch();
    }
    public TaskRouter getRouter() { return router; }
    @Override public String toString() { return "WorkflowEnvelope{router=" + router + "}"; }
}
