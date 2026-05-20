Feature: End-to-End Processing Pipeline

  Background:
    * url baseUrl
    * def sampleFilePath = 'classpath:data/sample_pdfs/sample_medical.pdf'

  Scenario: Full processing pipeline for a medical document
    
    # 1. Upload
    Given path 'upload'
    And multipart file file = { read: '#(sampleFilePath)', filename: 'sample_medical.pdf', contentType: 'application/pdf' }
    When method post
    Then status 200
    * def jobId = response.job_id
    
    # 2. Process
    Given path 'process', jobId
    When method post
    Then status 200
    And match response.message == 'Processing started in background.'
    
    # 3. Wait/Poll for Completion
    # In Karate we can use retry or sleep. sleep is simpler for simulated envs.
    * def sleep = function(millis){ java.lang.Thread.sleep(millis) }
    * sleep(3000)
    
    # 4. Check Classify API
    Given path 'classify', jobId
    When method get
    Then status 200
    And match response.intermediate_classification.predicted_category == 'medical_report'
    And match response.llm_classification.label == 'medical_report'
    
    # 5. Check Full Result API
    Given path 'result', jobId
    When method get
    Then status 200
    And match response.status == 'completed'
    And assert response.ocr_output.raw_text != ''
    And assert response.post_processing.cleaned_length > 0
    And match response.llm_classification.structured_entities == '#object'
    And match response.llm_classification.structured_entities.patient_name == 'Jane Smith'
