document.addEventListener('DOMContentLoaded', () => {
    const pressedKeyElement = document.getElementById('pressed-key');
    const keyDisplayElement = document.getElementById('key-display');
    const doorStatusElement = document.getElementById('door-status');
    let userSessionId = crypto.randomUUID();
    console.log(`User session ID: ${userSessionId}`);

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
