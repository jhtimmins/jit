JIT - Multiple Git Repo Command Line Tool
=========================================

JIT makes it easy to work on projects involving multiple different repositories. It works
with the assumption that the project is organized with a root directory containing all 
repositories for the project. The following are the available commands (prepended with `jit`):
  
**all**     Display all current branches.

**co \<branch name>**  Checks out this branch on all repos where it exists.

**dirty**   Display all repos with uncommitted changes.

**master**  Checkout master branch on all repos.

**mine**    Display all branches for all repos.

**pull**    Pull from remote origin on all repos. 

**show \<branch name>** Shows all repos where this branch exists.
