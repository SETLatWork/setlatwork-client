# SETL@Work client

The SETL@Work client is a wrapper for FME Desktop. It receives jobs from https://manager.setlatwork.com - passes them onto FME Desktop to run and passes the results back to the manager website.



To run:
```python setlatwork.py```

To compile:
- Windows: `python setup_exe.py py2exe`
- OSX    : `python setup_app.py py2app`

## Structure

```
  setlatwork.py
    main.py
    taskbaricon.py
      server.py
        job.py
  icon
  icon.ico
  setup_app.py
  setup_exe.py
  VERSION
  LICENSE
```