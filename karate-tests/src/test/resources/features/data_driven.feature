Feature: Data-Driven Multi-Document Testing

  Background:
    * url baseUrl
    * def sleep = function(millis){ java.lang.Thread.sleep(millis) }

  Scenario Outline: Process <doc_type> document and expect <expected_category>
    
    # 1. Upload
    Given path 'upload'
    And multipart file file = { read: '<file_path>', filename: '<filename>', contentType: 'application/pdf' }
    When method post
    Then status 200
    * def jobId = response.job_id
    
    # 2. Process
    Given path 'process', jobId
    When method post
    Then status 200
    
    # 3. Wait for result
    * sleep(2500)
    
    # 4. Verify category
    Given path 'result', jobId
    When method get
    Then status 200
    And match response.status == 'completed'
    And match response.llm_classification.label == '<expected_category>'

    Examples:
      | doc_type | filename                     | file_path                                                  | expected_category |
      | invoice  | sample_invoice.pdf           | classpath:data/sample_pdfs/sample_invoice.pdf | invoice           |
      | identity | sample_identity.pdf          | classpath:data/sample_pdfs/sample_identity.pdf| identity_document |
      | medical  | sample_medical.pdf           | classpath:data/sample_pdfs/sample_medical.pdf | medical_report    |
