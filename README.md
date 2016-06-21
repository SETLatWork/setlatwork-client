# Readme

The SETL@Work client is a wrapper for FME Desktop. It receives jobs from https://www.setlatwork.com - passes them onto FME Desktop to run and passes the results back to the manager website.

This code is released as open source for the viewing pleasure of SETL@Work users, in an effort to provide trust that the client running on their work machine contains no malicious components.

You may view the code, but have no rights to make changes to it or redistribute it. This is the intellectual property of SETL@Work Limited.

# Run

```python setlatwork.py```

# Compile

- Windows: `python setup_exe.py py2exe`
- OSX    : `python setup_app.py py2app`

# SETL@Work Directory Structure

```
  logs                > created on start - log file for the client is stored here - overwritten upon re-starting
  temp                > created on start - downloaded workspaces are stored here
  setlatwork.py
    main.py           > creates a dialog for entering login credentials
    taskbaricon.py    > creates the taskbar icon
      server.py       > checks periodically for jobs
        job.py        > runs jobs picked up from server
  icon                > OSX icon
  icon.ico            > WIN icon
  setup_app.py        > compile the client for OSX
  setup_exe.py        > compile the client for WIN
  VERSION             > client version
  LICENSE             > copyright 
```