# Task 36: Separate DEV build and use flow

## Current State

The project `aicage` actually consist of several repos on GH:

1. `aicage/aicage-image-base`: builds base images to package `ghcr.io/aicage/aicage-image-base`.
2. `aicage/aicage-image`: pulls config from releases of aicage-image-base` and builds images based on the former base
   images to `ghcr.io/aicage/aicage`.
3. `aicage/aicage`: the python user client which uses aicage and sometimes aicage-image-base images from the ghcr.io
   packages. It also pulls config from releases of the former 2 repos.
4. `aicage/aicage-image-util`: also builds images to a package, the python aicage uses them - but for this task they are
   secondary

> `aicage/aicage` is the current working dir, the other repos are locally available at `../$repo/`.

## Problem

The problem I am facing is that many small changes require building the full flow of images (or are easier to try out
this way ... sometimes I could circumvent this). But this may also result in users facing new "official" images more
often. And `aicage` python code checks for new images and suggests to update them.

As long as I am/was the only user getting many new image downloads was ok - as the dev I know why and have a reason.

But a normal aicage user is maybe not so happy about downloading a new 5GB image several times a week or even per day.

## Solution

Split of a new test flow of images and code versions.

So far I have not done that for ease of maintenance. A full change flow from a change in the bases until the python code
has new final images takes about30-4m mins now if nothing goes wrong. And with a separate flow I have to do that twice
sometimes, once for DEV/TEST and once for PROD.

But now I've reached the pointn where I should do this. Also when all things which go wrong during test releases are
fixed, then likely the prod release will run though without hickups.

## Why this is not so easy

The ghcr packages are backed into 3 projects - I took care to keep them somewhere central but none of these projects
atm have a flow of changing those central definitions for forks or test repos and packages.

## Contributors affected

I have on contributors yet, but would also wonder how they would set up their forks to test changes they make or how
they could live use changed versions. Also they would have to fork potentially several repos and handle the references
between them and packages.

## Let's discuss

I have ideas already, but want to hear your analysis and opinion on how I could best handle this.