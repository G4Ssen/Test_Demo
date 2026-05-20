Feature: End-to-End Pipeline Integration

  Background:
    * url baseUrl

  Scenario: Full pipeline — Invoice document
    # Step 1: Upload
    Given path '/upload'
    And multipart file file = { read: 'classpath:testdata/invoice_sample.pdf', filename: 'invoice.pdf', contentType: 'application/pdf' }
    When method POST
    Then status 202
    * def jobId = response.job_id
    And assert response.status == 'QUEUED'
    And match response.pages >= 1

    # Step 2: OCR processing
    Given path '/process/' + jobId
    When method POST
    Then status 200
    And assert response.status == 'PROCESSED'
    * def processedText = response.ocr_cleaned
    And assert processedText.length > 0

    # Step 3: Classify
    Given path '/classify/' + jobId
    When method POST
    Then status 200
    * def finalLabel = response.llm_classification.label
    * def confidence = response.llm_classification.confidence
    And match finalLabel == 'INVOICE'
    And assert confidence > 0.7

    # Step 4: Retrieve full result
    Given path '/result/' + jobId
    When method GET
    Then status 200
    And match response.status == 'CLASSIFIED'
    And match response.final_label == 'INVOICE'
    And match response.pipeline_stages == '#object'
    And match response.pipeline_stages.ocr.status == 'OK'
    And match response.pipeline_stages.post_processing.status == 'OK'
    And match response.pipeline_stages.intermediate_classification.status == 'OK'
    And match response.pipeline_stages.llm_classification.status == 'OK'

  Scenario: Full pipeline — Identity document
    Given path '/upload'
    And multipart file file = { read: 'classpath:testdata/identity_sample.pdf', filename: 'passport.pdf', contentType: 'application/pdf' }
    When method POST
    Then status 202
    * def jobId = response.job_id

    Given path '/process/' + jobId
    When method POST
    Then status 200

    Given path '/classify/' + jobId
    When method POST
    Then status 200
    And match response.llm_classification.label == 'IDENTITY'

  Scenario: Full pipeline — Report document
    Given path '/upload'
    And multipart file file = { read: 'classpath:testdata/report_sample.pdf', filename: 'report.pdf', contentType: 'application/pdf' }
    When method POST
    Then status 202
    * def jobId = response.job_id

    Given path '/process/' + jobId
    When method POST
    Then status 200

    Given path '/classify/' + jobId
    When method POST
    Then status 200
    And match response.llm_classification.label == 'REPORT'

  Scenario: Pipeline consistency — intermediate and LLM labels agree for high-confidence documents
    Given path '/upload'
    And multipart file file = { read: 'classpath:testdata/invoice_sample.pdf', filename: 'invoice.pdf', contentType: 'application/pdf' }
    When method POST
    Then status 202
    * def jobId = response.job_id

    Given path '/process/' + jobId
    When method POST
    Then status 200

    Given path '/classify/' + jobId
    When method POST
    Then status 200
    * def intLabel = response.intermediate_classification.label
    * def llmLabel = response.llm_classification.label
    * def highConfidence = response.llm_classification.confidence > 0.85
    # For high-confidence documents both classifiers must agree
    * if (highConfidence) karate.match(intLabel, llmLabel)

  Scenario: Result endpoint reflects completed_at timestamp after full pipeline
    Given path '/upload'
    And multipart file file = { read: 'classpath:testdata/invoice_sample.pdf', filename: 'invoice.pdf', contentType: 'application/pdf' }
    When method POST
    Then status 202
    * def jobId = response.job_id

    Given path '/process/' + jobId
    When method POST
    Then status 200

    Given path '/classify/' + jobId
    When method POST
    Then status 200

    Given path '/result/' + jobId
    When method GET
    Then status 200
    And match response.completed_at == '#notempty'
    And match response.created_at == '#notempty'
