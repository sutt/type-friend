document.addEventListener('DOMContentLoaded', () => {
    const pressedKeyElement = document.getElementById('pressed-key');
    const keyDisplayElement = document.getElementById('key-display');
    const doorStatusElement = document.getElementById('door-status');
    const mobileFormElement = document.getElementById('mobile-form');
    const mobileInputElement = document.getElementById('mobile-input');
    let userSessionId = crypto.randomUUID();
    console.log(`User session ID: ${userSessionId}`);

    // XXX: Detect if the device is likely a mobile device
    const isLikelyMobile = window.matchMedia("(pointer: coarse)").matches;

    let fadeInAndHoldTimeoutId = null;
    let fadeOutCleanupTimeoutId = null;

    // XXX: Centralized function to process the key, update UI, and send to server
    async function processAndSendKey(keyToSend) {
        // XXX: Ignore "Unidentified" keys or empty keys
        if (!keyToSend || keyToSend === "Unidentified") {
            console.log(`Key ignored by processAndSendKey: ${keyToSend}`);
            return;
        }

        console.log(`Processing key for server: ${keyToSend}`);
        // XXX: toLowerCase b/c runes font has no upper case for some letters
        pressedKeyElement.textContent = keyToSend.toLowerCase();

        // XXX: Key display visibility logic
        clearTimeout(fadeInAndHoldTimeoutId);
        clearTimeout(fadeOutCleanupTimeoutId);
        keyDisplayElement.classList.remove('is-fading-out');
        keyDisplayElement.classList.add('visible');

        fadeInAndHoldTimeoutId = setTimeout(() => {
            keyDisplayElement.classList.add('is-fading-out');
            fadeOutCleanupTimeoutId = setTimeout(() => {
                keyDisplayElement.classList.remove('visible');
                keyDisplayElement.classList.remove('is-fading-out');
            }, 3000); // XXX: Corresponds to fade-out duration in CSS
        }, 500); // XXX: Hold duration before fading

        // XXX: Server communication
        try {
            const response = await fetch('/keypress', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ key: keyToSend, uuid: userSessionId }),
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
                }, 500); // XXX: Delay to allow fade-out animation
            }
        } catch (error) {
            console.error('Error sending keypress event:', error);
        }
    }

    if (isLikelyMobile) {
        if (mobileFormElement) {
            mobileFormElement.style.display = 'block';
        }

        if (mobileInputElement) {
            // XXX: Prevent form submission on Enter key for the mobile input
            mobileInputElement.addEventListener('keydown', (event) => {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    // XXX: The global keydown listener will handle sending "Enter"
                }
            });

            // XXX: Use 'input' event for mobile to reliably get character data
            mobileInputElement.addEventListener('input', () => {
                const charTyped = mobileInputElement.value;
                if (charTyped) {
                    // XXX: Send each character as it's typed
                    // XXX: This assumes single character inputs are desired per 'input' event.
                    // XXX: For multi-character words, this would send them one by one.
                    processAndSendKey(charTyped.slice(-1)); // XXX: Send the last character typed
                    mobileInputElement.value = ''; // XXX: Clear input field after processing
                }
            });
        }
    }

    document.addEventListener('keydown', async (event) => {
        const key = event.key;
        console.log(`Keydown event: key='${key}', target='${event.target.id}', activeElement='${document.activeElement && document.activeElement.id}'`);

        if (isLikelyMobile && document.activeElement === mobileInputElement) {
            // XXX: On mobile, if focus is on our mobileInput:
            // XXX: Character inputs are handled by the 'input' event listener on mobileInputElement.
            // XXX: This 'keydown' listener should only process special keys (e.g., "Enter", "ArrowUp").
            if (key.length > 1 && key !== "Unidentified") { // XXX: e.g., "Enter", "ArrowUp"
                processAndSendKey(key);
            }
            // XXX: If key is "Unidentified" or a single character (e.g. "a", "1") from mobileInput,
            // XXX: we do nothing here; 'input' event handles characters, "Unidentified" is ignored by processAndSendKey.
            return; 
        }

        // XXX: For desktop, or mobile when mobileInput is not focused:
        // XXX: process all keys via keydown.
        // XXX: processAndSendKey will filter out "Unidentified".
        processAndSendKey(key);
    });
});
