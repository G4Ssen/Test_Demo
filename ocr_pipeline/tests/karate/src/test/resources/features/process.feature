Feature: OCR Processing Service Validation

  Background:
    * url baseUrl
    * def uploadResult = call read('classpath:common/helpers.feature@upload-and-get-job-id') { filePath: 'classpath:testdata/invoice_sample.pdf', fileName: 'invoice.pdf' }
    * def jobId = uploadResult.jobId

  Scenario: Process a valid queued job
    Given path '/process/' + jobId
    When method POST
    Then status 200
    And match response.status == 'PROCESSED'
    And match response.ocr_raw == '#notempty'
    And match response.ocr_cleaned == '#notempty'
    And match response.word_count == '#number'
    And match response.word_count > 0
    And match response.processing_time_ms == '#number'
    And match response.processing_time_ms >= 0

  Scenario: Response contains both raw and cleaned text fields
    Given path '/process/' + jobId
    When method POST
    Then status 200
    * def raw = response.ocr_raw
    * def cleaned = response.ocr_cleaned
    And assert cleaned.length > 0
    And assert raw.length > 0

  Scenario: Re-processing an already-processed job returns 409
    # First call — should succeed
    Given path '/process/' + jobId
    When method POST
    Then status 200
    # Second call — job is now PROCESSED, not QUEUED
    Given path '/process/' + jobId
    When method POST
    Then status 409
    And match response.detail contains 'PROCESSED'

  Scenario: Process with unknown job ID returns 404
    Given path '/process/00000000-0000-0000-0000-000000000000'
    When method POST
    Then status 404
    And match response.detail == 'Job not found'
