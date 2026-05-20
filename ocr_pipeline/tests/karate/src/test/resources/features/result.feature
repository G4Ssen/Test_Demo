Feature: Result Endpoint Validation

  Background:
    * url baseUrl

  Scenario: Result for a fully classified job returns complete structure
    * def uploadResult = call read('classpath:common/helpers.feature@upload-and-get-job-id') { filePath: 'classpath:testdata/invoice_sample.pdf', fileName: 'invoice.pdf' }
    * def jobId = uploadResult.jobId
    * call read('classpath:common/helpers.feature@process-a-job') { jobId: '#(jobId)' }
    * call read('classpath:common/helpers.feature@classify-a-job') { jobId: '#(jobId)' }

    Given path '/result/' + jobId
    When method GET
    Then status 200
    And match response.job_id == '#uuid'
    And match response.status == 'CLASSIFIED'
    And match response.filename == '#notempty'
    And match response.ocr_cleaned == '#notempty'
    And match response.final_label == '#notempty'
    And match response.confidence == '#number'
    And match response.pipeline_stages == '#object'
    And match response.pipeline_stages.ocr == { status: 'OK', duration_ms: '#number' }
    And match response.pipeline_stages.post_processing == { status: 'OK', duration_ms: '#number' }
    And match response.pipeline_stages.intermediate_classification == { status: 'OK', duration_ms: '#number' }
    And match response.pipeline_stages.llm_classification == { status: 'OK', duration_ms: '#number' }

  Scenario: Result for a QUEUED job returns 202
    * def uploadResult = call read('classpath:common/helpers.feature@upload-and-get-job-id') { filePath: 'classpath:testdata/invoice_sample.pdf', fileName: 'invoice.pdf' }
    * def jobId = uploadResult.jobId
    # Do NOT call /process — job remains QUEUED
    Given path '/result/' + jobId
    When method GET
    Then status 202
    And match response.detail contains 'processing'

  Scenario: Result for unknown job ID returns 404
    Given path '/result/deadbeef-dead-beef-dead-beefdeadbeef'
    When method GET
    Then status 404
    And match response.detail == 'Job not found'
