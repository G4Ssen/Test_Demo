Feature: Karate Gatling Load Simulation

  Background:
    * url baseUrl
    * def sampleFilePath = 'classpath:../../../src/data/sample_pdfs/sample_invoice.pdf'

  Scenario: Simulate multiple users uploading documents
    Given path 'upload'
    And multipart file file = { read: '#(sampleFilePath)', filename: 'sample_invoice.pdf', contentType: 'application/pdf' }
    When method post
    Then status 200
    * def jobId = response.job_id
    
    # Ideally, we would process here as well, but load testing the upload 
    # and job creation logic is a standard Gatling use-case.
    # Given path 'process', jobId
    # When method post
    # Then status 200
