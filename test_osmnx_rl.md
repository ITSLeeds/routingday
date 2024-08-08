# How to contribute to the repo


This is an example of a Quarto file for an idea.

``` python
import osmnx as ox
# Read-in OSM data for a 1 km radius around Leeds:
```

To create a Pull Request linked to an issue, you can run the following:

``` bash
gh issue create
gh issue develop <x> # where x is the issue number
# ... make your changes in the repo codebase, add new file etc
git add .
git commit -am 'Your commit message'
git push
gh pr create
```
