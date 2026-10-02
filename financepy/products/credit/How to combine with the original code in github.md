Q: how to copy a pyhton package, modify it and get the updates from the original pacakage without loosing my modification?


To copy a Python package, modify it, and pull in future updates from the original author without losing your changes, you should use Git forks combined with an editable pip installation (pip install -e).
Here is the exact step-by-step workflow to achieve this cleanly:
## 1. Fork and Clone the Package
Instead of downloading a static copy, use Git to maintain a live relationship with the original repository.

   1. Go to the original package's repository (e.g., on [GitHub](https://github.com/)) and click the Fork button. This creates a personal copy under your own account.
   2. Clone your forked repository to your local machine:
   
   git clone https://github.com
   cd PACKAGE_NAME
   
   
## 2. Install the Package in "Editable" Mode
If you install the package normally, Python copies the files into its internal site-packages directory, meaning changes to your local folder won't register.
Instead, install it using the -e (editable) flag:

pip install -e .

This tells Python to link directly to your active project folder. Any edits you make to the source code will immediately apply whenever you import the package in your scripts.
## 3. Make Your Custom Modifications
Create a new branch for safety, apply your changes, and commit them to your fork:

git checkout -b my-custom-features# ... edit the Python files with your changes ...
git add .
git commit -m "Added my custom modifications"
git push origin my-custom-features

## 4. Sync Updates from the Original Package
When the original author releases new features or bug fixes, you can merge them into your modified version using Git's upstream tracking.

   1. Link the original repository as a remote source named upstream (you only need to do this once):
   
   git remote add upstream https://github.com
   
   2. Fetch and merge the original updates into your custom branch whenever you want to sync:
   
   git fetch upstream
   git merge upstream/main
   
   (Note: Replace main with master or whichever branch the original author treats as their default).

## Dealing with Merge Conflicts
If the original author changed a line of code that you also modified, Git will flag a conflict. Open the affected files, choose which code to keep (or combine both), delete the conflict markers (<<<<<<<, =======, >>>>>>>), and commit the resolution:

git add .
git commit -m "Resolved merge conflicts with upstream updates"

If you want to get started, tell me:

* 
* What is the name of the Python package you want to modify?
* Is it hosted on GitHub, GitLab, or somewhere else?
* 

I can provide the specific URL paths or commands tailored to that package.

