# OCR Document Processing System (Simulation)

This project simulates a backend document processing pipeline based on OCR and Large Language Models (LLMs). It demonstrates a fully testable architecture validated by a comprehensive **Karate** API test suite.

## Architecture

The system is implemented using **FastAPI** (Python) and mimics an asynchronous event-driven workflow:

1. **Input Service**: Validates and uploads a PDF.
2. **OCR Service**: (Mocked) Simulates text extraction from the PDF.
3. **Post-Processing Service**: Cleans and normalizes the OCR'd text.
4. **Intermediate Classification**: Uses rule-based keyword matching to guess the document category.
5. **LLM Service**: (Mocked) Simulates sending the data to an LLM for final classification and structured data extraction.

## Getting Started

### Running the API (Docker)

```bash
docker-compose up --build
```
The API is available at `http://localhost:8000/docs` (Swagger UI).

### Running the API (Local Python)

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```

## Karate Testing Suite

The primary QA focus of this project is the **Karate API Testing Framework**. The test suite resides in the `karate-tests/` directory.

### Running Karate API Tests
Requires Java 17 and Maven.

```bash
cd karate-tests
mvn test
```
*Reports are generated in: `target/karate-reports/karate-summary.html`*

### Running Gatling Performance Tests

```bash
cd karate-tests
mvn gatling:test
```
*Gatling HTML reports are generated in the `target/gatling/` directory.*

## How Karate Improves This Architecture

As an AI System Architect and QA Engineer, I selected Karate because it provides unique value to asynchronous, multi-stage data pipelines:

1. **Test Coverage via Schema Validation**: Karate's built-in JSON matching makes it trivial to validate complex LLM output structures. Instead of writing dozens of Java/Python assertions, a single Karate `match` statement ensures our LLM mock (and real integration) adheres to the exact schema.
2. **Integration Reliability for Chained Calls**: OCR pipelines are stateful. Karate easily handles chaining API calls (Upload -> Extract Job ID -> Process -> Poll -> Verify Results) without the callback hell seen in JS frameworks or verbosity in RestAssured. 
3. **Data-Driven Robustness**: Testing document pipelines requires varying inputs (Invoice vs ID vs Medical). Karate's `Scenario Outline` natively parses our mock PDF inputs and dynamically validates the resulting LLM classification.
4. **CI/CD & Performance Readiness**: By sharing the exact same Gherkin definitions between Functional API testing and Gatling load testing, we eliminate test duplication while guaranteeing performance standards under load.
