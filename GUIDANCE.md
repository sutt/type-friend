- When running /run or /test commands make sure to activate the app's virtualenv within the command. This is because the aider chat environemnt is not environment in which the app runs. To do this activate python associated with the app inline in your bash commands, e.g.: `.venv/bin/python app/main.py`. 
    - Also do the same for working with other python scripts on the app, e.g. pip or pytest. For example to install libraries to the app environment use: `.venv/bin/pip install pytest` and to execute pytest do `.venv/bin/python -m pytest tests`.
- Commenting policy: Feel free to add comments but include the XXX prefix before all comments.
    - add "XXX: " prefix before all comments, e.g. `# XXX: this decrements the counter`
    - if the comment spans multiple lines, add the XXX prefix to each line 
    - do not use inline comments. If you must include the comment, add the comment on a new line
    - When writing docstrings, do not use the XXX prefix; write them normally.