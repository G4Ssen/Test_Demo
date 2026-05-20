Feature: Upload Endpoint Performance Baseline

  Scenario: Upload a PDF — used by Gatling load driver
    Given url baseUrl + '/upload'
    And multipart file file = { read: 'classpath:testdata/invoice_sample.pdf', filename: 'invoice.pdf', contentType: 'application/pdf' }
    When method POST
    Then status 202
