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

2.  **Backend (`main.py` - FastAPI application)**
    *   Serves the `index.html` page at the root (`/`).
    *   Serves static files from `/static`.
    *   **`/keypress` Endpoint (POST):**
        *   Receives `key` and `uuid` (the session UUID) from the client.
        *   Maintains a buffer of the most recent keypresses for each `uuid`. The buffer length is tied to the `SECRET_SPELL` length.
        *   Checks if the current buffer for a `uuid` matches a predefined `SECRET_SPELL`.
        *   If the spell matches, it flags that `uuid` as having successfully cast the spell by setting `user_access_granted[uuid] = True`.
        *   Returns a JSON response including `{"message": "...", "spell_successful": true/false}`.
    *   **`/protected_resource` Endpoint (GET):**
        *   Requires a `session_id` (which is the client's UUID) as a query parameter (e.g., `/protected_resource?session_id=xxxx-xxxx`).
        *   Checks if the provided `session_id` has successfully cast the spell by looking it up in the `user_access_granted` dictionary.
        *   If access is granted, returns a success message.
        *   If no `session_id` is provided, returns an HTTP 401 Unauthorized error.
        *   If `session_id` is provided but access is not granted (spell not cast or invalid `session_id`), returns an HTTP 403 Forbidden error.
    *   **State Management (In-Memory):**
        *   `SECRET_SPELL`: Loaded from an environment variable. The `python-dotenv` library is used to load this from a `.env` file if present in the application's root directory (e.g., `/app_container` in Docker). This string represents the sequence of keys to be pressed. A default value is used if not set.
        *   `user_key_buffers`: A Python dictionary storing the recent keypress history (as a list of characters) for each active user session UUID.
        *   `user_access_granted`: A Python dictionary storing boolean flags indicating whether a user session UUID has successfully cast the spell.
        *   Note: This state is in-memory and will be lost if the server restarts. For persistence, a database or other external store would be needed.
    *   **Configuration (`.env` file):**
        *   A `.env` file at the project root is used to store the `SECRET_SPELL`.
        *   An `.env.example` file provides a template.
        *   When running with Docker, the `Dockerfile` is configured to copy the `.env` file into the image. For production, consider injecting environment variables at runtime instead of bundling the `.env` file.

## Flow for Secret Spell

1.  User loads `index.html`.
2.  `script.js` generates a `userSessionId` (UUID) and stores it in a JavaScript variable for the duration of the page session.
3.  User presses keys.
4.  For each keypress, `script.js` sends `{ "key": "pressed_key", "uuid": "userSessionId" }` to the `/keypress` endpoint.
5.  The server's `/keypress` endpoint:
    a.  Retrieves or initializes the key buffer for `userSessionId`.
    b.  Appends the new key and trims the buffer.
    c.  Compares the buffer to `SECRET_SPELL`.
    d.  If they match, sets `user_access_granted[userSessionId] = True`.
    e.  Returns a JSON response, including `spell_successful` status.
6.  The client-side `script.js` receives the response. If `spell_successful` is true, it can then:
    a.  Modify the UI (e.g., show a link to the protected resource).
    b.  Automatically redirect to `/protected_resource?session_id=userSessionId`.
7.  When the client attempts to access `/protected_resource?session_id=userSessionId`:
    a.  The server's `/protected_resource` endpoint checks if `userSessionId` is in `user_access_granted` and is true.
    b.  Serves the protected content if access is granted, or an appropriate HTTP error otherwise.
