# RAG Platform Mission Completion and Codebase Guide

## Overview

This project has reached a strong functional milestone: a local end-to-end RAG pipeline is now working from document upload through grounded answer generation. The implemented flow covers document upload, PDF parsing, text chunking, embedding generation with Ollama, FAISS indexing, retrieval, and final RAG chat generation using retrieved context.[1][2][3]

The current design is also aligned with a production-minded architecture because each major concern is separated into its own layer: API routes, schemas, services, RAG processing modules, and infrastructure-style storage concerns. LangChain’s retrieval model emphasizes modular building blocks such as splitters, embeddings, vector stores, and retrievers, which matches the direction taken in this project even though the implementation uses direct code in several places for clarity.[1][4]

## What was built

The implemented system now supports the following application flow:[5][3][2]

1. An administrator uploads a PDF through the backend.
2. The backend stores the raw file on disk.
3. The parser reads the PDF and extracts text.
4. The chunker splits the parsed text into smaller sections.
5. The embedding step converts each chunk into a vector using Ollama embeddings.[5][6]
6. The indexing step stores vectors in a FAISS index for semantic retrieval.[2]
7. The retrieval step embeds the user query and finds the nearest chunks in the FAISS index.[2][7]
8. The RAG chat step sends the retrieved context plus the question to Ollama chat and returns a grounded answer.[3][8]

This means the system is no longer only an ingestion pipeline; it is already a working local RAG backend. The remaining work is mainly hardening, observability, better response contracts, and future database replacement such as Oracle Vector storage.[9][10]

## End-to-end workflow

The workflow can be understood as two separate pipelines: ingestion and question answering. Keeping these two pipelines separate is important because ingestion runs only when documents change, while retrieval and generation run every time a user asks a question.[1][8]

### Ingestion workflow

The ingestion pipeline transforms uploaded files into searchable knowledge.[5][2]

- Upload PDF
- Save raw file
- Parse file into extracted text
- Chunk the text
- Generate embeddings for chunks
- Index embeddings in FAISS

### Question-answer workflow

The chat pipeline transforms a user question into a grounded answer.[3][2][8]

- Accept user question
- Embed the query with the same embedding model used for documents.[5]
- Search FAISS for top similar chunks.[2][7]
- Build a prompt with retrieved context.[8][11]
- Send prompt to Ollama chat.[3]
- Return answer plus sources

## Why the package structure exists

A beginner often sees many folders and feels they are extra complexity, but each package exists to keep one kind of responsibility separate from another. This separation is the main reason the project is understandable, testable, and replaceable later.[1][10]

The current structure follows a common backend pattern where HTTP handling, validation, business logic, and AI processing are not mixed into one file. FastAPI request validation works especially well when schemas are separate from route functions, and retrieval systems are easier to evolve when chunking, embedding, and retrieval logic are separated from API code.[12][1]

## Folder-by-folder purpose

Below is the practical meaning of each major package in the project.

| Package or folder | Purpose | Why it exists |
|---|---|---|
| `app/api/routes/` | Defines HTTP endpoints such as upload, parser, chunker, embedding, indexing, retrieval, and rag chat. | Keeps web/API code separate from business logic so endpoints stay thin and readable.[12] |
| `app/schemas/` | Holds Pydantic request and response models. | FastAPI uses these for validation, Swagger docs, and clean typed contracts between client and backend.[12] |
| `app/services/` | Holds application logic such as save upload, parse file, chunk text, embed chunks, index data, retrieve matches, and generate RAG answers. | Keeps logic reusable and avoids writing all logic directly inside route handlers. |
| `app/rag/` | Holds lower-level AI helpers such as PDF loaders and chunkers. | Separates AI-specific processing internals from higher-level service orchestration. |
| `app/core/` | Stores configuration and shared app settings. | Centralizes environment-driven values such as model names, chunk sizes, and backend choices. |
| `data_resources/documents/raw/` | Raw uploaded files. | Preserves original documents for traceability and reparsing. |
| `data_resources/documents/parsed/` | Parsed JSON outputs from PDFs. | Makes parsing inspectable and reusable without rereading the source PDF every time. |
| `data_resources/documents/chunks/` | Chunked JSON outputs. | Lets chunking be debugged independently from parsing and embeddings. |
| `data_resources/documents/embeddings/` | Embedded JSON outputs. | Stores chunk + vector outputs before indexing or later migration to another vector backend. |
| `data_resources/vector_store/faiss/` | FAISS index and FAISS metadata. | Serves as the current local semantic retrieval backend.[2] |

## Why schemas are needed

Schemas are one of the most important parts for FastAPI beginners to understand. A schema is simply a contract that says what data is expected to come into an API endpoint and what data should go out of it; FastAPI uses Pydantic models for this request-body validation and documentation generation.[12]

For example, if `/parser/pdf` expects a field named `file_name`, then the schema enforces that and FastAPI returns `422` when the wrong field name is sent. This is exactly why the parser error happened earlier: the request body did not match the schema contract, so the backend rejected it before running business logic.[12]

### Why separate request and response schemas

Keeping request and response schemas explicit has several benefits:[12]

- clear Swagger documentation,
- automatic input validation,
- fewer runtime mistakes,
- easier frontend-backend integration,
- easier refactoring later.

A schema is not “extra code for no reason”; it is a safety boundary for the API.

## Why services are needed

A service contains the actual use-case logic. For example, the upload route should not know how to save files, the parser route should not know how PDF extraction works, and the retrieval route should not know all details of embedding and FAISS search. Those responsibilities belong to service classes and helper modules.[1][2]

This is why route files stay small while service files do the real orchestration. Later, when Oracle replaces FAISS, the route may stay almost unchanged while the service or repository implementation changes underneath it.

## Why some files are empty

Some files in a beginner-friendly backend repo are created early as placeholders so the package structure is ready before every feature is implemented. Empty files or lightly used files usually mean one of these things:

- the package was created for future extension,
- the architecture was prepared before implementation caught up,
- a folder needs `__init__.py` so Python treats it as a package,
- or a repository/service abstraction was planned before the real backend adapter was added.

This is normal in staged backend development. An empty file is not automatically a mistake, but if it is no longer needed, it should eventually be removed to reduce confusion.

## How a single request travels through the code

The easiest way to understand the codebase is to follow one request from start to finish.

### Example: document upload

1. Client calls `/documents/upload`.
2. Route function receives the request and validates the input type.
3. Route calls `DocumentService`.
4. `DocumentService` saves the file in `data_resources/documents/raw/`.
5. Route returns a schema-based JSON response.

### Example: parse request

1. Client calls `/parser/pdf` with a JSON body.
2. FastAPI validates the body against `DocumentParseRequest`.[12]
3. Route calls `ParserService`.
4. `ParserService` uses `PDFLoader` inside `app/rag/loaders/`.
5. Parsed text is saved into `data_resources/documents/parsed/`.
6. Route returns `DocumentParseResponse`.

### Example: retrieval request

1. Client calls `/retrieval/search` with a query.
2. FastAPI validates the body through the retrieval schema.[12]
3. `RetrievalService` embeds the query using Ollama embeddings.[5][6]
4. The FAISS index is loaded and searched for nearest vectors.[2][7]
5. Matching metadata rows are resolved.
6. The response returns ranked chunks and scores.

### Example: RAG chat request

1. Client calls `/rag/chat`.
2. Retrieval runs first to collect relevant chunks.
3. Retrieved chunk text is combined into a prompt context.[8][11]
4. The prompt and question are sent to Ollama `/api/chat`.[3]
5. The final response returns the generated answer plus sources.[13]

## Why the data is stored in stages

The project stores artifacts at multiple stages—raw, parsed, chunked, embedded, indexed—because this makes debugging and learning much easier. If a final answer is wrong, it becomes possible to inspect whether the problem started in parsing, chunking, embeddings, retrieval, or generation.[10]

This staged design also makes migration easier. For example, the current system uses FAISS, but the embedding artifacts and metadata structure can later be written into Oracle vector tables instead of a local index, without redesigning the earlier stages of the pipeline.[9][1]

## Current architecture summary

The current implementation can be summarized as follows.

| Layer | Current implementation | Replaceable later? |
|---|---|---|
| Web API | FastAPI routes + Pydantic schemas | Yes |
| File storage | Local filesystem | Yes |
| PDF parsing | PyMuPDF | Yes |
| Chunking | Recursive text splitting approach aligned with LangChain patterns | Yes[14] |
| Embeddings | Ollama embedding model | Yes[5] |
| Vector store | FAISS | Yes[2] |
| Generation model | Ollama chat model | Yes[3] |
| Enterprise vector DB | Not yet integrated; Oracle planned later | Yes[9] |

This means the system is already modular enough for future migration.

## What remains to complete the platform

The main remaining work is not to reinvent the whole architecture, but to improve production quality around the working backbone. The best next steps are:

- cleaner source-rich RAG responses,[13]
- prompt versioning and configuration traceability,[10][15]
- conversation history support,
- request/response logging and latency tracking in FastAPI,[16]
- document status and admin APIs,
- Oracle vector adapter later.[9]

## Beginner mental model

A useful beginner mental model is this:

- **routes** = doors into the application,
- **schemas** = rules about what can enter and leave through those doors,
- **services** = workers that do the real business job,
- **rag modules** = AI-specific tools used by the workers,
- **data folders** = saved outputs from each processing stage,
- **FAISS** = the temporary brain index for semantic search.[2]

When this mental model is clear, the repo becomes much easier to navigate.

## Final understanding

What was built is not just a chatbot endpoint but a modular local RAG backend that already demonstrates the main enterprise pattern: ingest knowledge once, retrieve relevant chunks per question, and ground LLM answers in retrieved context. The current FAISS-based implementation is a practical local substitute for a future enterprise vector database, and because the system is layered, Oracle can later replace the vector backend without forcing a redesign of upload, parsing, chunking, embeddings, retrieval contracts, or API shape.[1][2][9]