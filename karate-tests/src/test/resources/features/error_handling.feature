Feature: Error Handling Scenarios

  Background:
    * url baseUrl
    * def sleep = function(millis){ java.lang.Thread.sleep(millis) }

  Scenario: Attempt to process a non-existent job ID
    Given path 'process', 'invalid-uuid-1234'
    When method post
    Then status 404
    And match response.detail == 'Job not found'

  Scenario: Retrieve missing result
    Given path 'result', 'unknown-uuid-7890'
    When method get
    Then status 404
    And match response.detail == 'Job not found'
    
  Scenario: Upload empty/corrupted file
    Given path 'upload'
    And multipart file file = { read: 'classpath:data/sample_pdfs/error_corrupt.pdf', filename: 'error_corrupt.pdf', contentType: 'application/pdf' }
    When method post
    Then status 200
    * def jobId = response.job_id
    
    Given path 'process', jobId
    When method post
    Then status 200
    
    * sleep(2000)
    
    Given path 'result', jobId
    When method get
    Then status 200
    And match response.status == 'failed'
    And match response.error contains 'OCR failed to extract any text'
