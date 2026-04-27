# ITWS-4500-2H

`SyllabusAI` (or subjected to change) is an AI-Powered tool for comparing and analyzing the differences between cirriculums at different institutions. Just import the sources that you are comparing and it will generate you a side-by-side comparison as to how each program differs.

The application will point out strengths and weaknesses compared to what is currently being taught in course catalogs.


## In development:

Run `docker compose -f docker-compose.yml -f docker-compose.dev.yml up` for **development container**
- This routes the build to `docker-compose.dev.yml` which creates an image where you can see changes made to files instantly after saving without restarting the docker image.


Run `docker compose up` for regular usage / demos.

## Setup:

1. Create a `.env` file at the root directory, copy and paste the `.env.example` information and fill out the fields that are required
   - `GEMINI_API_KEY_1`
   - `GEMINI_API_KEY_2` (OPTIONAL)
   - `GROQ_API_KEY`
   - `NEXTAUTH_SECRET`
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_DB`
   - `SECRET_KEY`

2. Run `docker compose up`
 - Add `--build` to the end if you need to rebuild the application to update to current versions

### NOTE:
- Only users are allowed to currently create comparisons. So you must create an account and sign in in order for the comparison feature to work.
- You can view the layout of the pages, but cannot send API requests to the backend to retrieve data.