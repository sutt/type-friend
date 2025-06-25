# KeyPress Tracker with Secret Spell Access

## Overview

This application tracks keypresses from a web client and logs them on a FastAPI server. It includes a "secret spell" feature where a specific sequence of keypresses grants temporary access to a protected server resource for that user's session.

## Components

1.  **Frontend (`index.html`, `static/css/style.css`, `static/js/script.js`)**
    *   `index.html`: Basic HTML page to display the last pressed key.
    *   `style.css`: Basic styling.
    *   `script.js`:
        *   Generates a unique session ID (UUID) upon loading using `crypto.randomUUID()`.
        *   Listens for `keydown` events.
        *   Displays the pressed key on the page.
        *   Sends the pressed key and the session UUID to the `/keypress` endpoint on the server via a POST request.
        *   Receives a response from `/keypress` indicating if the spell was successful.
        *   (Client-side logic can then be used to enable access or redirect to the protected route, passing the session UUID).

2.  **Backend (`main.py` - FastAPI application, `app/key_buffer_manager.py` - Key Buffer Logic)**
    *   `main.py`:
        *   Serves the `index.html` page at the root (`/`).
        *   Serves static files from `/static`.
        *   **`/keypress` Endpoint (POST):**
            *   Receives `key` and `uuid` (the session UUID) from the client.
            *   Uses `KeyBufferManager` to add the key to the user's buffer and to check if the spell is cast.
            *   If the spell matches (case-insensitive comparison by `KeyBufferManager`), it flags that `uuid` as having successfully cast the spell by setting `user_access_granted[uuid] = True`.
            *   Returns a JSON response including `{"message": "...", "spell_successful": true/false}`.
        *   **`/protected_resource` Endpoint (GET):**
            *   Requires a `session_id` (which is the client's UUID) as a query parameter (e.g., `/protected_resource?session_id=xxxx-xxxx`).
            *   Checks if the provided `session_id` has successfully cast the spell by looking it up in the `user_access_granted` dictionary.
            *   If access is granted, returns a success message.
            *   If no `session_id` is provided, returns an HTTP 401 Unauthorized error.
            *   If `session_id` is provided but access is not granted (spell not cast or invalid `session_id`), returns an HTTP 403 Forbidden error.
    *   `app/key_buffer_manager.py`:
        *   Defines the `KeyBufferManager` class.
        *   This class is responsible for:
            *   Storing and managing keypress buffers for each user session.
            *   Trimming buffers to the length of the secret spell.
            *   Performing a case-insensitive comparison of a user's buffer against the configured secret spell.
    *   **State Management (In-Memory in `main.py` and `KeyBufferManager`):**
        *   `APP_SECRET_SPELL`: Loaded from an environment variable in `main.py`. This is a comma-separated string (e.g., "ArrowUp,ArrowUp,a,b,Enter").
        *   `PARSED_SECRET_SPELL`: The `APP_SECRET_SPELL` string is parsed into a list of key strings in `main.py` at startup. This list is then passed to the `KeyBufferManager` instance.
        *   `KeyBufferManager` instance (in `main.py`):
            *   Internally manages `user_key_buffers`: A dictionary storing recent keypress history for each user.
            *   Internally stores the `parsed_secret_spell` and its length (`_spell_key_count`) for buffer trimming and comparison.
        *   `user_access_granted` (in `main.py`): A Python dictionary storing boolean flags indicating whether a user session UUID has successfully cast the spell.
        *   Note: This state is in-memory and will be lost if the server restarts.
    *   **Configuration (`.env` file):**
        *   A `.env` file at the project root is used to store the `APP_SECRET_SPELL` as a comma-delimited string (e.g., `APP_SECRET_SPELL='key1,key2,Enter,key3'`).
        *   An `.env.example` file provides a template.
        *   When running with Docker, the `Dockerfile` is configured to copy the `.env` file into the image. For production, consider injecting environment variables at runtime instead of bundling the `.env` file.

## Flow for Secret Spell

1.  User loads `index.html`.
2.  `script.js` generates a `userSessionId` (UUID) and stores it in a JavaScript variable for the duration of the page session.
3.  User presses keys.
4.  For each keypress, `script.js` sends `{ "key": "pressed_key", "uuid": "userSessionId" }` to the `/keypress` endpoint.
5.  The server's `/keypress` endpoint (in `main.py`):
    a.  Calls the `KeyBufferManager` instance's `add_key` method, passing the `userSessionId` and the pressed key. The `KeyBufferManager` appends the key to the user's buffer and trims it to the configured spell length.
    b.  Calls the `KeyBufferManager` instance's `check_spell` method for the `userSessionId`. This method performs a case-insensitive comparison of the user's buffer against the stored secret spell.
    c.  If `check_spell` returns true, `main.py` sets `user_access_granted[userSessionId] = True`.
    d.  Returns a JSON response, including `spell_successful` status.
6.  The client-side `script.js` receives the response. If `spell_successful` is true, it can then:
    a.  Modify the UI (e.g., show a link to the protected resource).
    b.  Automatically redirect to `/protected_resource?session_id=userSessionId`.
7.  When the client attempts to access `/protected_resource?session_id=userSessionId`:
    a.  The server's `/protected_resource` endpoint checks if `userSessionId` is in `user_access_granted` and is true.
    b.  Serves the protected content if access is granted, or an appropriate HTTP error otherwise.
