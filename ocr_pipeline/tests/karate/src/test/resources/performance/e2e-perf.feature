Feature: End-to-End Pipeline Performance Baseline

  Scenario: Full Upload → Process → Classify pipeline — used by Gatling load driver
    # Step 1: Upload
    Given url baseUrl + '/upload'
    And multipart file file = { read: 'classpath:testdata/invoice_sample.pdf', filename: 'invoice.pdf', contentType: 'application/pdf' }
    When method POST
    Then status 202
    * def jobId = response.job_id

    # Step 2: Process
    Given url baseUrl + '/process/' + jobId
    When method POST
    Then status 200

    # Step 3: Classify
    Given url baseUrl + '/classify/' + jobId
    When method POST
    Then status 200

    # Step 4: Result
    Given url baseUrl + '/result/' + jobId
    When method GET
    Then status 200
