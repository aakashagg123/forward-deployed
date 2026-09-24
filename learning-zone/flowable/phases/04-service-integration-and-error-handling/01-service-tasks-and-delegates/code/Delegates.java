// Three ways to wire a service task to Java code, in one file.
//
//   1. flowable:class            — engine instantiates the class directly
//   2. flowable:delegateExpression — resolves a Spring bean implementing JavaDelegate
//   3. flowable:expression       — calls any bean method; no JavaDelegate needed
//
// Dependency: org.flowable:flowable-spring-boot-starter-process (see Phase 2, lesson 05).
package com.example.loans;

import org.flowable.engine.delegate.BpmnError;
import org.flowable.engine.delegate.DelegateExecution;
import org.flowable.engine.delegate.JavaDelegate;
import org.springframework.stereotype.Component;

public class Delegates {

    // Style 1: <serviceTask id="bureauCall" flowable:class="com.example.loans.Delegates$BureauCallDelegate"/>
    // The engine news it up per execution — no Spring injection available here.
    public static class BureauCallDelegate implements JavaDelegate {
        @Override
        public void execute(DelegateExecution execution) {
            String pan = (String) execution.getVariable("pan");
            int score = BureauGateway.fetchScore(pan);   // static access only

            // A *business* failure the model should route on -> BpmnError
            // (caught by an error boundary event, lesson 04). A technical
            // failure (bureau down) is just a thrown RuntimeException: the
            // transaction rolls back and the job retries (lesson 05).
            if (score == -1) {
                throw new BpmnError("NO_BUREAU_RECORD", "PAN has no bureau file");
            }
            execution.setVariable("score", score);
        }
    }

    // Style 2: <serviceTask id="bureauCall" flowable:delegateExpression="${bureauDelegate}"/>
    // A real Spring bean: constructor injection, @Transactional, the lot.
    // Preferred in Spring Boot apps.
    @Component("bureauDelegate")
    public static class SpringBureauDelegate implements JavaDelegate {
        private final BureauGateway gateway;

        public SpringBureauDelegate(BureauGateway gateway) {
            this.gateway = gateway;
        }

        @Override
        public void execute(DelegateExecution execution) {
            execution.setVariable("score",
                    gateway.score((String) execution.getVariable("pan")));
        }
    }

    // Style 3: <serviceTask id="bureauCall"
    //             flowable:expression="${bureauGateway.score(pan)}"
    //             flowable:resultVariable="score"/>
    // No delegate interface at all — the engine calls a plain bean method with
    // process variables as arguments and stores the return value.
    @Component("bureauGateway")
    public static class BureauGateway {
        public int score(String pan) {
            return fetchScore(pan);
        }

        static int fetchScore(String pan) {
            return pan == null ? -1 : 700 + (Math.abs(pan.hashCode()) % 150);
        }
    }
}
