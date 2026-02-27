# Task 34 - Add Podman support

Aicage depends heavily on Docker. But I've been in companies where Docker on (Windows) laptops was "forbidden" as the
company would have been required to buy licenses. We used Podman instead.

And as Podman is the only other options on desktop PC and laptops - I am considering adding support for Podman.

From what I know it's supposed to closely mirror docker on CLI commands - although I vaguely remember hitting some
differences.

## Part 1: Analyze what it would take

The Python library for Docker is only used in one module imho and there we can probably fall back to CLI Docker as in
many other places of the code.

The big question is:  
Are arguments to Podman CLI equals to Docker CLI? And how do we test this to be sure?  
The user base is too small to rely on bug reports - we must pretty much run all affected parts of the code in end-to-end
integration tests in the CLI with Podman to be sure.

Your task here is to thoroughly read each place in the code where we use Docker. And thoroughly read the Podman
documentation to check for equality.

Present me the results of your analysis for discussion, we decide here if we want to add Podman support.

## Part 2: Implement Podman support

Here we change the actual code. I expect a nice unit test coverage here - the rest of the code has 96% coverage.

## Part 3: Add end-to-end integration tests

As mentioned - each place in code must thoroughly be tested in near real life scenarios. We have such tests for Docker
already - if it must be we just run all a second time for Podman ... if it must be.

## Task workflow

- Don’t forget to read `AGENTS.md` and `doc/python-test-structure-guidelines.md` and respect those rules.
- Always use the existing venv.

You shall follow this order:

1. Read documentation and code to understand the task.
2. Ask me questions if something is not clear to you.
3. Present me with an implementation solution; this needs my approval.
4. Implement the change autonomously including a loop of running-tests, fixing bugs, running tests.
5. Run linters, use `scripts/lint.sh` with active venv.
6. Present me the change for review.
7. Interactively react to my review feedback.
8. Do not commit any changes unless explicitly instructed by the user.
