# Task 08: Better user information during image pull

In `src/aicage/registry/image_selection.py` we currently pull docker images silently.  
Without informing user or showing him any output from `docker pull` this leaves a user guessing for minutes why he sees 
nothing happening.

This needs fixing, the user should see:
- information what's going on like a text telling him that image is being pulled
- If we can do it nicely, he should see some sort of progress, one of:
  - raw docker output (not nice but simple)
  - A progress bar
  - A percentage counter
  - anything else which helps him estimate how much longer he has to wait

## Task Workflow

Don't forget to read AGENTS.md and always use the existing venv.

You shall follow this order:
1. Read documentation and code to understand the task. 
2. Aks me questions if something is not clear to you
3. Present me with an implementation solution - this needs my approval
4. Implement the change autonomously including a loop of running-tests, fixing bugs, running tests
5. Run linters as in the pipeline `.github/workflows/publish.yml`
6. Present me the change for review
7. Interactively react to my review feedback