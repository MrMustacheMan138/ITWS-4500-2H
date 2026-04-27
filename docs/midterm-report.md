SyllabusAI - Technical Progress Report
Jason, Akshat, Zhimin, Chloe, Mayge
Architecture Evolution:

Original: 
Frontend: React
Backend: Python, Node.js, FastAPI
Data: PostgreSQL
DevOps: Docker, GitHub, OAuth

Current:
Frontend: React, Tailwind
Backend: Python, Node.js, LangChain, FastAPI, PyMupdf, Pydantic, SQLAlchemy
Data: PostgreSQL, Python
DevOps: Docker, GitHub, OAuth

Changes:
Our current architecture has not changed significantly from the original plan. Most of the updates involved adding libraries and tools to support the implementation of specific features rather than redesigning the overall system.

Frontend:
We still maintained a clear separation between frontend and backend functionality.
Our original architectural diagram was fairly high-level, so we refined the frontend structure to make the codebase more modular and easier to manage
The smaller components such as the header, sidebar, forms, etc. are stored in their own subdirectories rather than being placed directly in the main application code
This improves code organization and makes these components easier to reuse across different parts of the application without duplicating code
We also structured the frontend in a way that allows components to be imported into the main display page more efficiently, following a clearer business-logic-oriented design.

Backend:
The backend followed a similar pattern. Like the frontend, the original design was fairly general, so we later developed a more detailed internal structure.
The backend is now divided into two main directories:
One handles the routes
The other handles core processing tasks such as data cleaning, retrieval-augmented generation (RAG) model operations, and database authentication
Under the route handler directory, there is a main script page where it establishes the routes of each component. Each API endpoint implementation is then separated into subdirectories based on the specific category or functionality that endpoint supports. This makes the backend easier to navigate, maintain, and extend.

Data model:
The data model underwent the most significant changes during development since it was very unclear at the start as to how we wanted to organize our data and create our pipeline to have our RAG model analyze the information into a well-structured table.
We introduced schemas to better organize the data being passed through the system and to ensure that each component receives data in a predictable and consistent structure. This allows the application to validate incoming data before it is processed.
If required fields are missing, the schema validation flags the issue and the affected component stops the execution. 
Similarly, if a field contains invalid or incorrectly formatted content, the system returns an error message. 
Adding schema validation tools has made the application more reliable and has helped ensure that each part of the system receives the correct data structure needed for processing.

Technical Challenges:
The extraction of the catalog data for a basic database prior to the transition to a LLM was not going smoothly. While the program name, course name, credit hours and linking courses to the programs that they were in worked fine, the extraction of the course description and prerequisite/corequisite did not work properly. Many times, it failed to extract specific information and when it did, the information went entirely into the prerequisite column of the table or the information was extracted to the next course row. We did not currently find a solution and we simply used what was working. As for the actual solution, we may need to rely on the use of a LLM if it is decided that we are to continue with including the course description and/or prerequisite/corequisite columns. 
The scope of how versatile our comparison model with the integrated LLM in our application posed a big problem as we expect it to do more work than feasible.
We wanted the LLM to clean the data, section it off into their significant sections and interpret the data all at once while also determining which type of data was being inputted (PDF, link, raw text data, etc). We basically wanted the LLM to do all the heavy work for us, but after research, that clearly isn’t possible. It would be too costly and there are too many uncertainties with that approach.
Solution: we decided to clean the data ourselves and have the comparisons rendered at a more supervised approach by the developers (us). When the application is actually pushed to production, the user is very limited as to what they can upload as a source (only parsable PDFs and links). But on the other hand, they will have all of the data there on hand to access. There will be drop -downs that will contain pre-loaded data about each institution and their course. The user can pick which institution, program, and year they want to compare. The sources will be loaded, data will be retrieved, and the table that will be presented will appear in a clean set-up. The AI’s 
suggestion and comments regarding the two courses will appear at the bottom and will also generate a score for the two courses.

Implementation Status:
Currently, our application has these following features implemented:
Frontend styling and layout completed
- All hyperlink buttons work
User authentication
- User sessions
Dashboard display
Some API endpoints initialized and implemented
- Authentication endpoints initialized and communicating with the database
Database connected and initialized
Schemas to validate form data in both the front and backend

Features in progress:
Rest of the API endpoints on the backend - all initialized, just need logic to be implemented
POST endpoint for sending sources for comparison
Response with formatted data to display on the frontend
GET endpoint to get all of the user saved compare sessions
Going to be across the entire application, so will be needed for Dashboard, Comparisons, Sources, and AI Chat
Data chunking based off of specific HTML tags in documents/sources that are submitted - almost done, need to refine the logic, and test
This is for the comparison page
Implementing prompting script for the LLM - missing, need to start implementing
This is for comparison page + AI chatbot page
Need to implement the sources page - not started yet, will need other features that add data into the database first

Features deferred:
Features based on user session
Deferred because this is a feature that would be “nice to have” and wouldn’t affect too much as to how our application works in our final presentation demo
There are also too many other features that are in progress right now to address this and this is low priority currently since we don’t have our application published to a user base
Rate limiting on AI Chats and AI Comparisons
Again, this is a nice to have feature and we have other high priority features to implement for the final presentation before addressing this issue
	We plan to start running tests and quality metrics soon. We have been focusing on getting as many pieces of the main body completed so that we can go back and touch up the details later. Once we have the backend and general idea of the RAG model down, we will start running more tests. The only tests we’ve run so far are for authentication for the user and other frontend style features.

Project Management Review:
The team operated in two informal sprints over roughly 7 weeks. The first sprint (Jan 27 – Feb 27) focused on project setup — initializing the repo, setting up the base architecture, auth structure, and database. The second sprint (Mar 1 – Mar 17) focused on feature implementation — Docker setup, backend routing, ingestion endpoints, frontend UI pages, and database catalog work. So far, this schedule has been very accurate and fair. Even though we are a little bit behind this plan, we are almost done with the second sprint and ready to begin the third. 
Key decisions that were made along the way were choosing to switch from a full RAG/LLM implementation to a simpler structured data approach to keep the project scope manageable, and prioritizing the creation of a working demo over completing the AI features within the first half of the project.
	We have not been utilizing the Projects feature on GitHub as mentioned in the initial proposal document, but we have several opened Github Issues with set milestones and due dates. While the first two sprints had slow progress, we plan to do a hard push for the remaining two sprints of the project.

	Regarding the velocity/burndown data, we did not use Scrum so no such burndown data exists. Based on the GitHub commit history, we can see that the majority of active development happened between March 6–17, with velocity picking up significantly closer to the midterm deadline. The chart below shows the contribution activity per member over the project timeline.

Path to Final: 
Remaining work:
Finish implementing backend endpoints for all necessary calls (3-7 days)
Connecting frontend features with data retrieved from backend processes (1-2 days)
Fully develop the RAG model, schemas for input and output, and finish the data cleaning scripts (2-3 weeks, 14 - 21 days)
Regarding the timeline, we are currently in the 2nd phase of the project where we are working on curriculum data collection and traditional structured comparison. 

Updated timeline:
Finish the 2nd phase (now - March 27th)
The 3rd phase (March 28th - April 20th) involves the implementation of RAG-based and agentic AI analysis. 
The final phase (April 21th - April 27th) involves the validation of our findings and preparation of the final documentation and presentation. 

The project was meant to allow anyone to look up and compare curriculum information between any two colleges, but upon looking through some of the college’s online curriculum, the project may need to go through some potential adjustments. Due to how some of the online curriculum info seem to follow a different format, we may need to either find a LLM that can extract the needed info no matter the format or limit the links in which the LLM will extract info from or create a script to parse through data, section information found through raw HTML using tags and other keys and develop a universal format for our script to pass through to the LLM. However, if the format of the data is not parsable through the scripts that we develop or is not parsable by the AI that we implement, we will need to log an error and send the user an error message.
	Current risks include LLM extraction inaccuracies, and large data processing times. Regarding LLM extraction inaccuracies such as hallucinations, these risks will be mitigated by enforcing strict structured outputs using schemas. The LLM will be prompted to ensure that its response will match a predefined Pydantic schema. If the LLM’s output does not match the schema, it will be rejected or corrected before being stored. The risk of large data processing times will be mitigated via data preprocessing and not repeating duplicate requests. Large pdfs will be split up into smaller sections before processing so that processing requests do not take an unreasonable amount of time. Additionally we will ensure that we do not process the same data multiple times, by maintaining a record of what pages/PDFs have already been processed. 
	After reviewing our current resources being used and the scope of our project, we have determined that we are going to adjust our approach to a simpler structured data method. To recap, our original scope was to create an AI-powered app that uses and validates user-provided data, URLs, multiple document types, or text copied from official course websites, supports multiple document types commonly used by universities, extracts curriculum information, and generates a side by side comparison between two universities. However, due to challenges with handling different document formats and inconsistencies in extracted data, we decided to focus more on structured and reliable data sources. This allows us to more accurately extract curriculum information and generate cleaner comparisons. The system will still generate a rigor score and display the information in a way that is presented in a structured and readable format for the user.
