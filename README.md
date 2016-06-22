# Readme

The SETL@Work client is a wrapper for FME Desktop. It receives jobs from https://www.setlatwork.com and passes them to FME Desktop to run, before sending the results back to the website.

This code is released as open source for the confidence of SETL@Work users. In an effort to provide transparency as to the workings of the client application.

You may view the code and execute it, but have no right to make changes or redistribute it. By downloading this code you also accept our terms and conditions found on our website: https://www.setlatwork.com/page/4/terms%20and%20conditions

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
    main.py           > creates a dialog for entering login and fme location
    taskbaricon.py    > creates the taskbar icon with menu
      server.py       > checks the setlatwork webiste periodically for jobs
        job.py        > runs jobs picked up from server
  icon                > OSX icon
  icon.ico            > WIN icon
  setup_app.py        > compile the client for OSX
  setup_exe.py        > compile the client for WIN
  VERSION             > version
  LICENSE             > copyright 
```