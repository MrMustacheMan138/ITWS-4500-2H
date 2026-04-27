 AI-Driven Curriculum Benchmarking Tool Project Proposal
Group 2-H: Akshat Prakash, Chloe Lee, Mayge Cheung, Jason Zheng, Zhimin Jiang

Executive Summary:
Universities frequently ask, “How does our program compare to peer institutions?” Today, answering that question is slow and manual—administrators and faculty must dig through many course catalogs, degree requirement pages, and track descriptions just to form a rough comparison. Our web application turns curriculum benchmarking into a clear, data-driven process by collecting official program documents, structuring the requirements and course coverage, and generating side-by-side comparisons across institutions. On top of this, a citation-grounded AI assistant produces curriculum gap analyses and summaries that link directly to catalog language and official sources, allowing users to verify claims quickly. Instead of relying on guesswork, scattered notes, or uncited summaries, stakeholders get fast, trustworthy insights on where a program is stronger, weaker, or missing coverage.

Problem Statement:
In the past, program administrators have faced significant challenges in comparing their academic programs and curricula against peer institutions. Administrators and faculty spend excessive time manually reviewing course catalogs, degree requirements, and track descriptions to perform basic curriculum comparisons. This process is not only time-consuming but also prone to inaccuracies, inefficiencies, and sometimes a lack of transparency. As higher education institutions continue to face more pressure to modernize, there is a critical need for a streamlined, data-driven system that can centralize and compare course offerings across institutions. This would ultimately help universities improve their programs and align them with emerging trends in teaching, technology, and student demand.

Here is some evidence that the problem exists:
Market Data on Tool Adoption:
According to research from ListEdTech, there has been a significant increase in the adoption of “Catalog Management” tools since 2010. Historically, universities relied on static PDFs or printed catalogs, leading to inefficiencies. The shift toward digital “Curriculum Management” and “Catalog Management” systems addressed the issue to eliminate manual data entry, streamline workflows, and ensure the accuracy of course offerings.
Case Study for NYU Curriculum Management Overhaul (2025):
At NYU, faculty members revealed frustrations with the reliance on disparate spreadsheets, manual routing of documents, and the inefficiency of finding the latest course catalog versions. In response, NYU is implementing CourseLeaf CIM to improve workflows, track new course proposals, and streamline administrative updates. This directly supports the need for more efficient tools to modernize curriculum management.
Talk with Prof. DiTursi:
In an office hour meeting with Prof. Ditursi, he expressed his challenges in adapting to teaching new courses. Recently, he has taken on the role of teaching two classes for the first time: Computer Architecture & Operating System (CAOS) and Intro to Algorithms. He had expressed that coordinating the schedule of these unfamiliar courses is particularly difficult, as he must create a comprehensive syllabus that covers all necessary content while maintaining an appropriate pace. He also mentioned that organizing a well-structured course requires constant adaptation and often relies heavily on advice and guidance from colleagues to ensure the course meets both academic standards and student needs.
While there are tools like Modern Campus and Leepfrog Technologies, they fail in providing tools for comparing curriculums across institutions. Most of these platforms focus on internal inefficiencies, so there is a gap in allowing institutions to benchmark their curriculum against peer institutions in a structured, side-by-side format. Our product will bridge this gap and centralize the data for cross-institution comparisons, while allowing universities to compare their course rigor, content coverage, and overall structure. With the addition of an AI assistant, it will highlight gaps in curriculums as well.

Proposed Solution:
Description: 
This project is an AI-powered tool that enables university administrators to analyze and compare the academic rigor of STEM programs using verifiable curriculum data. Rather than relying on generalized rankings or subjective impressions, the application generates structured comparisons directly from official course materials such as syllabi, catalogs, and program webpages provided by the user. 
The system allows administrators to upload or link documents from two institutions, after which an AI pipeline extracts key curricular features and presents them in parallel tables. Every statement produced by the model is backed by a direct citation to the original source, ensuring transparency and preventing hallucinated claims. The goal is to provide a practical decision-support tool that helps institutions evaluate their own programs against peer universities and identify opportunities for curricular improvement.

Core Features:
User-Provided Data Ingestion:
Accepts URLs, PDFs, or text copied from official course websites
Supports multiple document types commonly used by universities
Validation of data on the imported source (i.e. verifying if it’s the right institution)

AI Curriculum Extraction:
Identifies structured elements such as:
Required courses and electives
Prerequisite chains
Credit distribution
Assessment style and workload indicators
Concentration/specialization pathways

Side-by-side Comparison Interface:
Generates two parallel tables representing each institution
Sections appear only if supported by the uploaded documents
Key differences are highlighted

Citation Design:
Every important sentence is linked to a quoted source
Users can trace claims back to original document

Rigor Score:
Produces a transparent score based on:
Course depth
Prerequisite complexity
Credit intensity
Assessment structure

User Stories:
University Administrator - I want to compare my institution’s Computer Science program with a peer school so that I can identify gaps in course offerings and prerequisite structure.
Head of CS Department - I want to see how another University structures its concentrations so that I can refine our specialization tracks and elective options.
Academic Advisor - I want AI-generated comparisons with cited sources that I can justify curriculum changes to faculty committees using verifiable data.
Differentiation from Existing Solutions:
Current platforms such as U.S. News provide high-level rankings on reputation, selectivity, and broad institutional metrics. These tools do not examine the actual academic content that defines a program’s rigor.
How our application differs:
Deep Curriculum Focus - instead of general statistics, the system analyzes course-level information, prerequisite pathways, and concentration structures.
User-Controlled Data - the user supplies the exact documents they want analyzed, ensuring relevance and accuracy rather than relying on scraped third-party summaries. The model will also save data and over-time will be trained on accumulated data in-case users don’t know where to look for specific information and the model already has it on hand.
Citation-Driven - Every generated insight links directly to its source, allowing users to verify claims and explore documents in greater depth.

Technical Architecture:
System architecture diagram:
The system includes four layers: (1) ingestion of official curriculum sources, (2) normalization into a structured database, (3) comparison services, and (4) a citation-grounded AI (RAG) layer
Official sources include university catalogs, degree requirement pages, and track/concentration descriptions from institutional websites	
An ingestion pipeline snapshots pages/documents, extracts text, and parses courses and requirement rules
Normalized data is stored in a relational database for consistent cross-institution comparisons
A vector retrieval index is built from source passages so AI outputs are grounded and cited
The web app calls backend APIs to display comparisons and AI-generated gap analyses with a “show sources” view

Technology stack with justification:
Frontend: Next.js (React) for a fast, modern UI for program selection, comparisons, and citation display
Backend: FastAPI (Python) for ingestion, parsing, comparison logic, and RAG endpoints
Database: PostgreSQL for structured curriculum entities and query-based comparison
Vector retrieval: pgvector (or similar) to retrieve source passages for cited AI outputs
Document storage: S3-compatible storage for raw source snapshots and traceability
Authentication: OAuth (Google/Microsoft) or email/password for MVP, with optional role-based access

Data model overview:
Institution: name, catalog year, base URL
Program: institution, degree type, program name
Track: program, track name, description
Course: institution, code, title, credits, description
RequirementBlock/Item: structured degree requirements (core/electives/credits) and rule text
CourseMapping: cross-school “similar/equivalent” course links with confidence
SourceDocument/Citation: stored sources and evidence snippets used for verification and AI citations

API design approach:
Comparison endpoint returns requirement and coverage differences between programs
REST API endpoints for program discovery, curriculum retrieval, and comparisons
AI endpoints provide gap analysis and chatbot Q&A using RAG
All AI outputs must include citations; if evidence is insufficient, the system returns an “insufficient source support” response

Authentication and security considerations:
Rate limiting on AI endpoints to prevent abuse and control cost
Input validation and sanitization on all endpoints
Authentication via OAuth or email/password; optional admin/editor roles for ingestion management
Hallucination mitigation via retrieval-only generation and citation-required outputs
Only official public documents are ingested; no sensitive student data is collected

Deployment strategy:
Basic logging/monitoring to track ingestion failures and citation coverage
Backend deployed as a containerized service (Render/Fly.io/AWS)
Managed Postgres (Neon/Supabase/AWS RDS) and object storage for source snapshots
Scheduled or manual ingestion refresh to handle catalog updates

Project Management Plan:
Team roles and responsibilities:
Jason Zheng - Backend Development
Chloe Lee - Frontend Development
Akshat Prakash - DevOps
Mayge Cheung - Database
Zhimin Jiang -  Backend or Frontend Development

Project management tool choice (GitHub Projects, Jira, etc.):
GitHub Projects will be used for task and milestone tracking.
Integrated with version control to support transparency and accountability
Kanban-style boards will help manage task progress.
GitHub Issues will assign tasks, track completion, and document decisions. 

Sprint/milestone breakdown:
Sprint 1: Project planning, schema definition, and peer institution selection
Sprint 2: Curriculum data collection and traditional structured comparison
Sprint 3: Implementation of RAG-based and agentic AI analysis
Sprint 4: Validation of findings and preparation of final documentation

Risk identification and mitigation:
Incomplete or inconsistent data mitigated by using only official institutional documents
AI hallucinations or uncited claims mitigated by enforcing citation-required outputs
Timeline or scope risks mitigated through clearly defined roles and regular milestone reviews
Timeline and Milestones:

Sprint 1 (Week 1 - 4): Project Foundation and Planning
Define the project scope, goals, and primary user story.
Design the database schema and overall system architecture.
Select the peer institutions that will be used for curriculum comparison.
Prepare and deliver the initial project proposal and presentation.

Sprint 2 (Week 5 - 9): Data and Frontend Development
Collect and organize curriculum and course data from selected institutions.
Build structured comparison features for courses, requirements, and focus areas.
Develop and finalize the frontend interface using real or sample data.
Ensure all core pages, navigation, and features are functional.

Sprint 3 (Week 10 - 13): AI Integration and Backend Development
Implement RAG-based and agentic AI for curriculum analysis.
Connect the frontend to the backend database and AI services.
Enable AI-generated comparisons and curriculum gap analysis.
Test full system integration to ensure everything works together.

Sprint 4 (Week 14- 16): Testing and Final Presentation
Validate the accuracy of comparisons and AI-generated insights.
Refine the interface, fix bugs, and improve performance.
Prepare final documentation and user instructions.
Deliver the final presentation and live demo of the completed system.
