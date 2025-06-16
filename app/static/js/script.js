document.addEventListener('DOMContentLoaded', () => {
    const pressedKeyElement = document.getElementById('pressed-key');
    const keyDisplayElement = document.getElementById('key-display');
    const doorStatusElement = document.getElementById('door-status');
    const testInputElement = document.getElementById('test-input'); // XXX: Get the test input element
    let userSessionId = crypto.randomUUID();
    console.log(`User session ID: ${userSessionId}`);

    // XXX: Prevent form submission on Enter key for the temporary test input
    if (testInputElement) {
        testInputElement.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                // XXX: Optionally, you might want to blur the input or do something else
                // XXX: console.log('Enter pressed in test input, submission prevented.');
            }
        });
    }

    // XXX: Get the hidden input field for mobile keyboard
    const mobileKeyboardTrigger = document.getElementById('mobile-keyboard-trigger');
    // XXX: Detect if the device is likely a mobile device (has coarse pointer, e.g., touch)
    const isLikelyMobile = window.matchMedia("(pointer: coarse)").matches;

    if (isLikelyMobile && mobileKeyboardTrigger) {
        // XXX: Set initial focus to the hidden input on mobile to bring up the virtual keyboard
        mobileKeyboardTrigger.focus();

        // XXX: Add a click listener to the body to re-focus the hidden input
        // XXX: if the user taps on a non-interactive part of the page.
        document.body.addEventListener('click', (event) => {
            const targetElement = event.target;
            // XXX: Re-focus if the click is not on the input itself, a button, a link,
            // XXX: or an element within a button or link.
            if (targetElement !== mobileKeyboardTrigger &&
                targetElement.tagName !== 'BUTTON' &&
                targetElement.tagName !== 'A' &&
                !targetElement.closest('button') &&
                !targetElement.closest('a')
               ) {
                mobileKeyboardTrigger.focus();
            }
        });
    }

    let fadeInAndHoldTimeoutId = null;
    let fadeOutCleanupTimeoutId = null;

    document.addEventListener('keydown', async (event) => {
        const key = event.key;
        console.log(`Key pressed: ${key}`);
        pressedKeyElement.textContent = key.toLowerCase();
        //toLowerCase b/c runes font has no upper case for some letters

        clearTimeout(fadeInAndHoldTimeoutId);
        clearTimeout(fadeOutCleanupTimeoutId);

        keyDisplayElement.classList.remove('is-fading-out');
        keyDisplayElement.classList.add('visible');

        fadeInAndHoldTimeoutId = setTimeout(() => {
            keyDisplayElement.classList.add('is-fading-out');

            fadeOutCleanupTimeoutId = setTimeout(() => {
                keyDisplayElement.classList.remove('visible');
                keyDisplayElement.classList.remove('is-fading-out');
            }, 3000);
        }, 500);

        try {
            const response = await fetch('/keypress', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ key: key, uuid: userSessionId }),
            });

            if (!response.ok) {
                console.error('Failed to send keypress event to server:', response.statusText);
                return;
            }

            const result = await response.json();
            console.log('Server response:', result);

            if (result.spell_successful) {
              if (doorStatusElement) {
                  doorStatusElement.classList.add('is-fading-out');
              }
              setTimeout(() => {
                  const protectedButton = document.getElementById('protected-link');
                  if (protectedButton) {
                     protectedButton.style.display = 'block';
                     protectedButton.onclick = function() {
                        window.location.href = `/protected_resource?session_id=${userSessionId}`;
                     };
                  }
              }, 2000);
            }
        } catch (error) {
            console.error('Error sending keypress event:', error);
        }
    });
});
