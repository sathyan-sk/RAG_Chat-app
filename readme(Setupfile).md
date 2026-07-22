# RAG Application Setup Guide

This guide explains how to run the current RAG application locally, verify the automated document ingestion flow, and hand the project over to a team for further enhancement. The FastAPI application structure is intended to use separate router modules with `APIRouter` and register them in the main app with `include_router()`, which is the standard multi-file organization pattern for larger FastAPI projects.[1][2]

## Project Scope

The current application is designed around an automated ingestion lifecycle for PDF documents. A document is uploaded once, then the backend can automatically run parsing, chunking, embedding, and indexing in the background by using FastAPI background tasks after the upload response is returned.[3][4]

The intended flow is: "AUTOMATED ingestion"

- Upload PDF through `/documents/upload`
- Create a `document_id`
- Start background ingestion....
- Move through statuses such as `uploaded`, `parsing`, `chunking`, `embedding`, `indexing`, and `indexed`
- Use indexed documents for retrieval in chat

## Prerequisites

Install these before running the application:

- Python 3.10 or later
- `pip` or `uv`
- A virtual environment tool such as `venv`
- FAISS-compatible environment for vector indexing
- Any PDF parsing dependencies required by the existing `PDFLoader`
- Any embedding backend required by `EmbeddingProvider`, such as Ollama if the project uses a local embedding model


## Initial Local Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-project-folder>
```

### 2. Create and activate a virtual environment

On Linux or macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

If using `requirements.txt`:

```bash
pip install -r requirements.txt
```

If using `pyproject.toml`:

```bash
pip install -e .
```

At minimum, the project will typically need FastAPI, Uvicorn, Pydantic, NumPy, and FAISS, along with any PDF and embedding libraries used by the current services.

### 4. Create required folders

If they do not already exist, create these directories:

```bash
mkdir -p data_resources/documents/raw
mkdir -p data_resources/documents/parsed
mkdir -p data_resources/documents/chunks
mkdir -p data_resources/documents/embeddings
mkdir -p data_resources/vector_store/faiss
```

These folders are system-managed storage for the ingestion pipeline and should not be used as a manual upload area once the API-driven workflow is in place.


## Run the Application

Start the API server with Uvicorn:

```bash
uvicorn main:app --reload
```

If your `main.py` is inside a package, run the correct import path, for example:

```bash
uvicorn app.main:app --reload
```

Once started, FastAPI will expose interactive API docs, typically at:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Automated Ingestion Flow

The application is intended to support this operational workflow:

1. Client uploads a PDF to `/documents/upload`
2. API stores the file and creates a registry record
3. API returns immediately with `document_id`
4. A FastAPI background task starts the ingestion pipeline
5. The pipeline parses, chunks, embeds, and rebuilds the index
6. The document becomes available to chat only after indexing completes


## Manual API Test Steps

Use the Swagger UI or any API client.

### 1. Upload a PDF

Endpoint:

```http
POST /documents/upload
```

Form field:

- `file`: PDF file

Expected response shape:

```json
{
  "document_id": "uuid-value",
  "original_filename": "sample.pdf",
  "stored_filename": "uuid-value.pdf",
  "status": "uploaded",
  "message": "Document uploaded successfully. Processing started."
}
```

### 2. Check document status

Endpoint:

```http
GET /documents/{document_id}
```

Expected status progression:

- `uploaded`
- `parsing`
- `chunking`
- `embedding`
- `indexing`
- `indexed`

If anything fails, the status should become `failed` and the registry should store an error message.

### 3. List all documents

Endpoint:

```http
GET /documents/
```

This should show all known document records, including current processing state.

### 4. Test retrieval chat

After at least one document reaches `indexed`, test the RAG chat endpoint, for example:

```http
POST /rag/chat
```
Use a question that clearly matches content from the uploaded PDF.

## Multi-Document Verification

To confirm multiple documents are supported, run this sequence:

1. Upload PDF A
2. Wait until A becomes `indexed`
3. Upload PDF B
4. Wait until B becomes `indexed`
5. Ask a chat question that could retrieve content from either document

This works because the indexing service is expected to rebuild the vector index from all active embedded documents, not just the latest uploaded file.

## Understanding Points

For the team taking over the project, these are the current responsibilities of each area:

| Area | Responsibility |
|------|----------------|
| `documents.py` | Upload, list, and get document status |
| `document_service.py` | Save uploaded PDFs and create registry records |
| `document_registry_service.py` | Track lifecycle status and activation state |
| `ingestion_pipeline_service.py` | Orchestrate automated ingestion |
| `parser_service.py` | Convert uploaded PDF into parsed JSON |
| `chunking_service.py` | Convert parsed text into chunks |
| `embedding_service.py` | Generate embeddings per chunk |
| `indexing_service.py` | Rebuild FAISS index from active embedded documents |
| `rag.py` | Query retrieval and answer generation |

## Known Current Limits

At the current stage, this setup is enough to run the project and let a team continue enhancement, but it is not yet a final production architecture.

Current improvement candidates:

- Add retry endpoint for failed ingestion
- Add soft delete endpoint for documents
- Add locking around concurrent index rebuilds
- Add a dedicated worker queue if ingestion volume grows
- Add UI polling for document status
- Add retrieval filtering so only indexed-ready documents are used

FastAPI background tasks are useful for lightweight and moderate asynchronous work, but heavier workloads often move to a more dedicated job-processing pattern later while keeping the same application flow.[4]

## Troubleshooting issues if any cuase

### Upload works but document never reaches indexed

Possible causes:

- embedding backend is not running
- PDF parser failed
- chunk file was not generated
- FAISS dependency is missing or incompatible
- background task raised an exception and the document moved to `failed`

Check:

- application logs
- document registry JSON file
- parsed, chunks, embeddings, and index output folders

### Chat does not answer from newly uploaded files

Possible causes:

- document is still processing
- indexing did not complete
- retrieval endpoint is not reading the rebuilt FAISS metadata
- chat service is not filtering for active indexed documents correctly

## Operational Summary

For the current phase, the setup is sufficient if these conditions are met:

- the application starts successfully
- upload returns a `document_id`
- background ingestion runs automatically
- document status can be inspected through API endpoints
- indexed documents can be used by chat
- multiple documents can coexist in the same data source pipeline

That is enough for a team to take over and evolve the project into a more complete working application.