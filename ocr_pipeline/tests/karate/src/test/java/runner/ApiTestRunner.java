package runner;

import com.intuit.karate.junit5.Karate;

class ApiTestRunner {

    /** Run ALL feature files (excluding @ignore scenarios). */
    @Karate.Test
    Karate testAll() {
        return Karate.run("classpath:features")
                     .tags("~@ignore")
                     .relativeTo(getClass());
    }

    /** Dedicated runner for the end-to-end pipeline scenario. */
    @Karate.Test
    Karate testEndToEnd() {
        return Karate.run("classpath:features/end-to-end")
                     .relativeTo(getClass());
    }

    /** Dedicated runner for error-handling and edge-case scenarios. */
    @Karate.Test
    Karate testErrorHandling() {
        return Karate.run("classpath:features/error-handling")
                     .relativeTo(getClass());
    }
}
