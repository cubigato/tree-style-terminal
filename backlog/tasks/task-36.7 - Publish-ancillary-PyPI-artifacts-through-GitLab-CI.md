---
id: TASK-36.7
title: Publish ancillary PyPI artifacts through GitLab CI
status: To Do
assignee: []
created_date: '2026-07-23 13:17'
updated_date: '2026-07-23 23:39'
labels:
  - packaging
  - pypi
  - release
  - gitlab
dependencies:
  - TASK-36.6
references:
  - 'https://packaging.python.org/en/latest/tutorials/packaging-projects/'
  - 'https://docs.pypi.org/trusted-publishers/'
  - 'https://pygobject.gnome.org/guide/sysdeps.html'
modified_files:
  - pyproject.toml
  - .gitlab-ci.yml
  - README.md
parent_task_id: TASK-36
priority: medium
ordinal: 3500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
As a post-1.0 distribution convenience, publish the pure-Python source distribution and wheel as an ancillary channel for developers and downstream packagers without presenting PyPI as a complete Linux desktop installation. Integrate publication with the later GitLab release workflow and document the unavoidable external GTK, PyGObject, and VTE requirements. This task does not block the Debian or AppImage release.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The source distribution and wheel contain all importable application resources, have consistent current metadata, and pass standard package checks.
- [ ] #2 Installation documentation clearly states that PyPI cannot install or resolve the required GTK3 and VTE system libraries and does not provide reliable system desktop integration.
- [ ] #3 TestPyPI publication and installation are verified before enabling production PyPI publication, and the public project name is confirmed under cubigato control.
- [ ] #4 Production publication occurs only from a protected release job using the safest authentication mechanism supported for the self-hosted GitLab environment, with no credentials embedded in the repository or artifacts.
- [ ] #5 Published PyPI versions correspond exactly to tagged releases and are not described as the recommended installation route for regular Linux desktop users.
<!-- AC:END -->
