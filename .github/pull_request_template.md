# Description

* Short description here *

closes *Add ticket reference here*

# Merge procedure

Don't use the github built-in merge, but the process described [here](https://docs.internal.inmanta.com/topics/tasks/commiting_changes_modules.html)

```sh
git pull
git checkout master
git pull
git merge --squash issue/{issue-number}-{short description}
inmanta module commit -m "{Commit Message Here}" -r
git push
git push {tag} # push the tag as well
```

Then close the PR with a reference to the commit

# Self Check:

Strike through any lines that are not applicable (`~~line~~`) then check the box

- [ ] Attached issue to pull request
- [ ] Changelog entry
- [ ] Version number is bumped to dev version
- [ ] Code is clear and sufficiently documented
- [ ] Sufficient test cases (reproduces the bug/tests the requested feature)
- [ ] Correct, in line with design
- [ ] End user documentation is included or an issue is created for end-user documentation (add ref to issue here: )
