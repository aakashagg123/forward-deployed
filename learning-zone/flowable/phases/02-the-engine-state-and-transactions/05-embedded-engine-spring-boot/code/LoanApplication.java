// A complete embedded-Flowable Spring Boot app in one file.
//
// Dependencies (pom.xml):
//   org.flowable:flowable-spring-boot-starter-process:7.1.0
//   com.h2database:h2 (or your real JDBC driver)
//
// Put loan-triage.bpmn20.xml in src/main/resources/processes/ — the starter
// auto-deploys everything in that folder on startup.
package com.example.loans;

import java.util.Map;

import org.flowable.engine.RuntimeService;
import org.flowable.engine.TaskService;
import org.flowable.engine.delegate.DelegateExecution;
import org.flowable.engine.delegate.JavaDelegate;
import org.flowable.task.api.Task;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Component;

@SpringBootApplication
public class LoanApplication {

    public static void main(String[] args) {
        SpringApplication.run(LoanApplication.class, args);
    }

    // A service task implemented as a Spring bean. In the model:
    //   <serviceTask id="creditCheck" flowable:delegateExpression="${creditCheckDelegate}"/>
    // The delegate runs INSIDE the engine's transaction (lesson 03 applies:
    // throw here and the whole segment rolls back).
    @Component("creditCheckDelegate")
    public static class CreditCheckDelegate implements JavaDelegate {
        @Override
        public void execute(DelegateExecution execution) {
            long amount = (Long) execution.getVariable("amount");
            execution.setVariable("score", amount < 1_000_000 ? 720 : 640);
        }
    }

    // Drive one instance end-to-end on startup, using the same two operations
    // as the toy engine: start (advance until asleep) and complete (wake).
    @Bean
    CommandLineRunner demo(RuntimeService runtimeService, TaskService taskService) {
        return args -> {
            String id = runtimeService.startProcessInstanceByKey(
                    "loanTriage", Map.of("applicant", "meera", "amount", 2_000_000L))
                    .getId();

            Task review = taskService.createTaskQuery()
                    .processInstanceId(id).singleResult();
            System.out.println("waiting at: " + review.getName());

            taskService.complete(review.getId(), Map.of("decision", "approved"));
            System.out.println("instance ended: "
                    + (runtimeService.createProcessInstanceQuery()
                           .processInstanceId(id).count() == 0));
        };
    }
}
