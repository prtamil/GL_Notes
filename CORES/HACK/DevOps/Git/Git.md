# Git Rebase vs Merge 

(Merge vs Rebase)[https://www.atlassian.com/git/tutorials/merging-vs-rebasing]
(git Tutorials)[https://www.atlassian.com/git/tutorials]

Merge: 
   1. Creates new commits on target combines all feature commits 

Rebase:
   1. ReWrites commit history of feature in front of main.


# Git force fully merge from one branc to another
source: => seotweaks
target: => master
## Approach 1
```
git checkout master
git pull                    #uptodate local
git checkout seotweaks      #uptodate ourbranch local
git pull
git merge -s ours master    # -statergy=ours
git checkout master         # switch to target
git merge seotweaks         # merge
```

## Approach 2
Make sure everything is pushed up to your remote repository (GitHub):

```
git checkout main
```

Overwrite "main" with "better_branch":

```
git reset --hard better_branch
```

Force the push to your remote repository:

```
git push -f origin main
```