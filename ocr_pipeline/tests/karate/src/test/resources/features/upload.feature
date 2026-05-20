Feature: Upload Service Validation

  Background:
    * url baseUrl

  # ── Happy paths ─────────────────────────────────────────────────────────────

  Scenario: Upload a valid invoice PDF
    Given path '/upload'
    And multipart file file = { read: 'classpath:testdata/invoice_sample.pdf', filename: 'invoice.pdf', contentType: 'application/pdf' }
    When method POST
    Then status 202
    And match response contains { job_id: '#uuid', status: 'QUEUED', filename: 'invoice.pdf', pages: '#number', created_at: '#string' }
    And match response.pages >= 1

  Scenario: Upload multi-page identity document
    Given path '/upload'
    And multipart file file = { read: 'classpath:testdata/identity_sample.pdf', filename: 'passport.pdf', contentType: 'application/pdf' }
    When method POST
    Then status 202
    And match response.status == 'QUEUED'
    And match response.job_id == '#uuid'

  Scenario: Upload returns unique job IDs for separate requests
    Given path '/upload'
    And multipart file file = { read: 'classpath:testdata/invoice_sample.pdf', filename: 'invoice.pdf', contentType: 'application/pdf' }
    When method POST
    Then status 202
    * def jobId1 = response.job_id
    Given path '/upload'
    And multipart file file = { read: 'classpath:testdata/invoice_sample.pdf', filename: 'invoice.pdf', contentType: 'application/pdf' }
    When method POST
    Then status 202
    * def jobId2 = response.job_id
    And assert jobId1 != jobId2

  # ── Error paths ─────────────────────────────────────────────────────────────

  Scenario: Reject unsupported file type (text/plain)
    Given path '/upload'
    And multipart file file = { read: 'classpath:testdata/invoice_sample.pdf', filename: 'fake.txt', contentType: 'text/plain' }
    When method POST
    Then status 400
    And match response.detail contains 'Unsupported file type'

  Scenario: Reject oversized file (> 20 MB)
    Given path '/upload'
    And multipart file file = { read: 'classpath:testdata/oversized.pdf', filename: 'big.pdf', contentType: 'application/pdf' }
    When method POST
    Then status 413
    And match response.detail contains 'exceeds'

  Scenario: Reject corrupted PDF
    Given path '/upload'
    And multipart file file = { read: 'classpath:testdata/corrupted.pdf', filename: 'corrupted.pdf', contentType: 'application/pdf' }
    When method POST
    Then status 400
    And match response.detail contains 'corrupted'

  Scenario: Reject empty request body (missing file field)
    Given path '/upload'
    And request {}
    When method POST
    Then status 422
