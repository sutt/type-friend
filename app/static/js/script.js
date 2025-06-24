document.addEventListener('DOMContentLoaded', () => {
    const pressedKeyElement = document.getElementById('pressed-key');
    const keyDisplayElement = document.getElementById('key-display');
    const doorStatusElement = document.getElementById('door-status');
    const mobileFormElement = document.getElementById('mobile-form');
    const mobileInputElement = document.getElementById('mobile-input');
    const hintFieldElement = document.getElementById('hint-field');
    let userSessionId = crypto.randomUUID();
    console.log(`User session ID: ${userSessionId}`);

    const isLikelyMobile = window.matchMedia("(pointer: coarse)").matches;

    let fadeInAndHoldTimeoutId = null;
    let fadeOutCleanupTimeoutId = null;

    function highlightMatchingChar(key) {
        if (!hintFieldElement) return;
        
        hintFieldElement.innerHTML = 'friend - enter';
        
        const text = 'friend - enter';
        const normalizedKey = key.toLowerCase();
        
        let matchIndex = -1;
        if (normalizedKey === 'enter') {
            matchIndex = text.indexOf('enter');
            if (matchIndex !== -1) {
                const beforeMatch = text.substring(0, matchIndex);
                const match = 'enter';
                const afterMatch = text.substring(matchIndex + 5);
                hintFieldElement.innerHTML = `${beforeMatch}<span style="color: yellow;">${match}</span>${afterMatch}`;
            }
        } else if (normalizedKey.length === 1) {
            matchIndex = text.indexOf(normalizedKey);
            if (matchIndex !== -1) {
                const beforeMatch = text.substring(0, matchIndex);
                const match = text.charAt(matchIndex);
                const afterMatch = text.substring(matchIndex + 1);
                hintFieldElement.innerHTML = `${beforeMatch}<span style="color: yellow;">${match}</span>${afterMatch}`;
            }
        }
    }

    async function processAndSendKey(keyToSend) {
        if (!keyToSend || keyToSend === "Unidentified") {
            return;
        }

        // toLowerCase because font doesnt have upper case for some letters
        pressedKeyElement.textContent = keyToSend.toLowerCase();

        highlightMatchingChar(keyToSend);

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
                            window.location.href = `/mines?session_id=${userSessionId}`;
                        };
                    }
                }, 500);
                // Hide error message if spell is successful
                const errorElement = document.getElementById('error-message');
                if (errorElement) {
                    errorElement.style.display = 'none';
                }
            } else if (result.message && result.message.includes('already cast the spell')) {
                // Display IP blocking error message
                const errorElement = document.getElementById('error-message');
                if (errorElement) {
                    errorElement.textContent = result.message;
                    errorElement.style.display = 'block';
                }
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
            mobileInputElement.addEventListener('keydown', (event) => {
                if (event.key === 'Enter') {
                    event.preventDefault();
                }
            });

            // Use 'input' event for mobile to reliably get character data
            mobileInputElement.addEventListener('input', () => {
                const charTyped = mobileInputElement.value;
                if (charTyped) {
                    processAndSendKey(charTyped.slice(-1));
                    mobileInputElement.value = '';
                }
            });
        }
    }

    document.addEventListener('keydown', async (event) => {
        const key = event.key;
        console.log(`Keydown event: key='${key}', target='${event.target.id}', activeElement='${document.activeElement && document.activeElement.id}'`);

        if (isLikelyMobile && document.activeElement === mobileInputElement) {
            // This 'keydown' listener should only process special keys (e.g., "Enter", "ArrowUp").
            if (key.length > 1 && key !== "Unidentified") {
                processAndSendKey(key);
            }
            return; 
        }
        processAndSendKey(key);
    });
});
