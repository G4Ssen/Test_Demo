Feature: Classification Service Validation

  Background:
    * url baseUrl

  Scenario: Intermediate and LLM classification return valid structure
    * def uploadResult = call read('classpath:common/helpers.feature@upload-and-get-job-id') { filePath: 'classpath:testdata/invoice_sample.pdf', fileName: 'invoice.pdf' }
    * def jobId = uploadResult.jobId
    * call read('classpath:common/helpers.feature@process-a-job') { jobId: '#(jobId)' }

    Given path '/classify/' + jobId
    When method POST
    Then status 200
    And match response.job_id == '#uuid'
    And match response.status == 'CLASSIFIED'
    And match response.intermediate_classification == { label: '#string', method: 'RULE_BASED', matched_keywords: '#array', confidence: '#number' }
    And match response.llm_classification == { label: '#string', confidence: '#number', reasoning: '#string', model: '#string', tokens_used: '#number' }

  Scenario: LLM confidence is within valid range [0.0, 1.0]
    * def uploadResult = call read('classpath:common/helpers.feature@upload-and-get-job-id') { filePath: 'classpath:testdata/invoice_sample.pdf', fileName: 'invoice.pdf' }
    * def jobId = uploadResult.jobId
    * call read('classpath:common/helpers.feature@process-a-job') { jobId: '#(jobId)' }

    Given path '/classify/' + jobId
    When method POST
    Then status 200
    * def conf = response.llm_classification.confidence
    And assert conf >= 0.0 && conf <= 1.0

  Scenario: Classification label is from the allowed set
    * def uploadResult = call read('classpath:common/helpers.feature@upload-and-get-job-id') { filePath: 'classpath:testdata/report_sample.pdf', fileName: 'report.pdf' }
    * def jobId = uploadResult.jobId
    * call read('classpath:common/helpers.feature@process-a-job') { jobId: '#(jobId)' }

    Given path '/classify/' + jobId
    When method POST
    Then status 200
    * def allowedLabels = ['INVOICE', 'IDENTITY', 'REPORT', 'CONTRACT', 'UNCLASSIFIED']
    And match allowedLabels contains response.llm_classification.label
    And match allowedLabels contains response.intermediate_classification.label

  Scenario: Re-classifying an already-classified job returns 409
    * def uploadResult = call read('classpath:common/helpers.feature@upload-and-get-job-id') { filePath: 'classpath:testdata/invoice_sample.pdf', fileName: 'invoice.pdf' }
    * def jobId = uploadResult.jobId
    * call read('classpath:common/helpers.feature@process-a-job') { jobId: '#(jobId)' }
    * call read('classpath:common/helpers.feature@classify-a-job') { jobId: '#(jobId)' }
    # Second classify attempt
    Given path '/classify/' + jobId
    When method POST
    Then status 409
    And match response.detail contains 'CLASSIFIED'
