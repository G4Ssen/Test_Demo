Feature: Error Handling and Edge Cases

  Background:
    * url baseUrl

  Scenario: Process endpoint with invalid UUID format returns 422
    Given path '/process/not-a-valid-uuid'
    When method POST
    Then status 422

  Scenario: Classify before processing (wrong state) returns 409
    Given path '/upload'
    And multipart file file = { read: 'classpath:testdata/invoice_sample.pdf', filename: 'invoice.pdf', contentType: 'application/pdf' }
    When method POST
    Then status 202
    * def jobId = response.job_id
    # Skip /process — jump straight to /classify
    Given path '/classify/' + jobId
    When method POST
    Then status 409
    And match response.detail contains 'QUEUED'

  Scenario: Result for unknown job ID returns 404
    Given path '/result/deadbeef-dead-beef-dead-beefdeadbeef'
    When method GET
    Then status 404
    And match response.detail == 'Job not found'

  Scenario: Upload with missing file field returns 422 with validation errors
    Given path '/upload'
    And request { }
    When method POST
    Then status 422
    And match response.detail == '#array'

  Scenario: Error response structure is consistent (single detail string)
    Given path '/upload'
    And multipart file file = { read: 'classpath:testdata/invoice_sample.pdf', filename: 'bad.txt', contentType: 'text/plain' }
    When method POST
    Then status 400
    And match response == { detail: '#string' }
    And match response.detail == '#notempty'

  Scenario: Process endpoint with non-existent UUID returns 404
    Given path '/process/ffffffff-ffff-ffff-ffff-ffffffffffff'
    When method POST
    Then status 404
    And match response.detail == 'Job not found'

  Scenario: Classify endpoint with non-existent UUID returns 404
    Given path '/classify/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    When method POST
    Then status 404
    And match response.detail == 'Job not found'

  Scenario: Health endpoint always returns 200
    Given url baseUrl.replace('/api/v1', '')
    And path '/health'
    When method GET
    Then status 200
    And match response.status == 'ok'
