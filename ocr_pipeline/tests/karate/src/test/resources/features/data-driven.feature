Feature: Data-Driven Multi-Document Testing

  Background:
    * url baseUrl

  # ── Scenario Outline with Examples table ───────────────────────────────────

  Scenario Outline: Classify <filename> and verify expected label '<expected_label>'
    # Upload
    Given path '/upload'
    And multipart file file = { read: 'classpath:testdata/<filename>', filename: '<filename>', contentType: 'application/pdf' }
    When method POST
    Then status 202
    * def jobId = response.job_id

    # Process
    Given path '/process/' + jobId
    When method POST
    Then status 200
    And match response.ocr_cleaned == '#notempty'

    # Classify
    Given path '/classify/' + jobId
    When method POST
    Then status 200
    And match response.llm_classification.label == '<expected_label>'
    And assert response.llm_classification.confidence >= <min_confidence>

    Examples:
      | filename              | expected_label | min_confidence |
      | invoice_sample.pdf    | INVOICE        | 0.80           |
      | identity_sample.pdf   | IDENTITY       | 0.75           |
      | report_sample.pdf     | REPORT         | 0.70           |

  # ── karate.forEach bulk test ───────────────────────────────────────────────

  Scenario: Bulk classify all sample documents via karate.forEach
    * table docs
      | filename              | expectedLabel |
      | invoice_sample.pdf    | INVOICE       |
      | identity_sample.pdf   | IDENTITY      |
      | report_sample.pdf     | REPORT        |
    * def testDoc =
      """
      function(doc) {
        var uploadRes = karate.call(
          'classpath:common/helpers.feature@upload-and-get-job-id',
          { filePath: 'classpath:testdata/' + doc.filename, fileName: doc.filename }
        );
        var jobId = uploadRes.jobId;
        karate.call('classpath:common/helpers.feature@process-a-job', { jobId: jobId });
        var classifyRes = karate.call(
          'classpath:common/helpers.feature@classify-a-job', { jobId: jobId }
        );
        var actualLabel = classifyRes.response.llm_classification.label;
        karate.log('Doc:', doc.filename, '→ Label:', actualLabel, '(expected:', doc.expectedLabel + ')');
        karate.match(actualLabel, doc.expectedLabel);
      }
      """
    * def ignored = karate.forEach(docs, testDoc)
