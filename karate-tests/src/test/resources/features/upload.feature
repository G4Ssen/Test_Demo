Feature: Upload API

  Background:
    * url baseUrl
    * def sampleFilePath = 'classpath:data/sample_pdfs/sample_invoice.pdf'

  Scenario: Upload a valid PDF file
    Given path 'upload'
    And multipart file file = { read: '#(sampleFilePath)', filename: 'sample_invoice.pdf', contentType: 'application/pdf' }
    When method post
    Then status 200
    And match response == 
    """
    {
      job_id: '#string',
      filename: 'sample_invoice.pdf',
      file_size_bytes: '#number',
      page_count: '#number',
      status: 'pending',
      message: '#string'
    }
    """
    And assert response.file_size_bytes > 0
    And assert response.job_id.length > 10
