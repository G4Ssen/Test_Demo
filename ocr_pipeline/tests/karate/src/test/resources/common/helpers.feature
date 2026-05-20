@ignore
Feature: Reusable helper scenarios (called via karate.call)

  # ── Upload a PDF and return jobId ──────────────────────────────────────────
  @upload-and-get-job-id
  Scenario: upload and get job id
    Given url baseUrl + '/upload'
    And multipart file file = { read: '#(filePath)', filename: '#(fileName)', contentType: 'application/pdf' }
    When method POST
    Then status 202
    And match response.job_id == '#uuid'
    And match response.status == 'QUEUED'
    * def jobId = response.job_id

  # ── Trigger OCR processing ─────────────────────────────────────────────────
  @process-a-job
  Scenario: process a job
    Given url baseUrl + '/process/' + jobId
    When method POST
    Then status 200
    And match response.status == 'PROCESSED'
    And match response.ocr_cleaned == '#notempty'

  # ── Trigger classification ─────────────────────────────────────────────────
  @classify-a-job
  Scenario: classify a job
    Given url baseUrl + '/classify/' + jobId
    When method POST
    Then status 200
    And match response.status == 'CLASSIFIED'
