# ITWS-4500-2H

`SyllabusAI` (or subjected to change) is an AI-Powered tool for comparing and analyzing the differences between cirriculums at different institutions. Just import the sources that you are comparing and it will generate you a side-by-side comparison as to how each program differs.

The application will point out strengths and weaknesses compared to what is currently being taught in course catalogs.


## In development:

Run `docker compose -f docker-compose.yml -f docker-compose.dev.yml up` for development container
- This routes the build to `docker-compose.dev.yml` which creates an image where you can see changes made to files instantly after saving without restarting the docker image.


Run `docker compose up` for regular usage / demos.