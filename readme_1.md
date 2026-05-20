# Project Review: OCR Document Processing Pipeline

## 📊 Overview & Review
This project is an advanced, robust, and well-architected asynchronous data pipeline designed to handle document uploads, perform Optical Character Recognition (OCR), and classify documents using both rule-based engines and Large Language Models (LLMs).

**Key Strengths:**
1. **Modern Stack:** The use of FastAPI for high-performance async routing, combined with heavy-duty libraries like PyMuPDF, OpenCV, and Tesseract, makes this a production-grade OCR pipeline.
2. **Resilience & Scalability:** The architecture clearly separates concerns into distinct services (`input_service`, `ocr_service`, `llm_service`). The use of Redis for result storage and the inclusion of Gatling for load testing show that this system is built to scale.
3. **World-Class QA Approach:** The decision to use **Karate** for API testing is phenomenal. Karate is perfect for this event-driven, stateful architecture where tests need to upload a file, grab a `job_id`, poll for completion, and strictly validate complex JSON schema outputs from an LLM.

---

## 📁 Understanding the Test Directories

You might have noticed that there are **two** separate test folders in your workspace. This can be confusing at first, but it represents a very professional "mock-first" architectural approach. Here is why both exist:

### 1. The Root `karate-tests/` Folder
**Location:** `C:\Users\Ghassen\.gemini\antigravity\scratch\karate-tests\`
**Purpose:** This folder tests the **simulated/mocked** version of your pipeline (found in the root `src/` folder).
- **Why it exists:** Before building the heavy, expensive integration with real OCR and OpenAI, a lightweight proxy was built to validate the *architecture* and the *tests themselves*. This allows developers to test the CI/CD pipeline, API routing, and state management instantly without paying for OpenAI API calls or waiting for heavy Tesseract processing.

### 2. The `ocr_pipeline/tests/` Folder
**Location:** `C:\Users\Ghassen\.gemini\antigravity\scratch\ocr_pipeline\tests\`
**Purpose:** This folder contains the tests for the **real, full implementation** of the pipeline (found in the `ocr_pipeline/` folder).
- **Why it exists:** This is the production-ready code. The Karate tests inside this directory (`ocr_pipeline/tests/karate`) are designed to run against the actual OCR engine, the real OpenCV pre-processing, and the actual Redis datastore. It includes a `generate_testdata.py` script to create physical PDFs to feed into the real Tesseract engine.

### Summary
- Use the root `karate-tests/` alongside `docker-compose up` to test the **fast, mocked simulation** (great for architectural testing and CI/CD setup).
- Use `ocr_pipeline/tests/karate` to validate the **actual computer vision and AI logic** before deploying to production.
