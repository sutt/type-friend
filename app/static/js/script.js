document.addEventListener('DOMContentLoaded', () => {
    const pressedKeyElement = document.getElementById('pressed-key');
    let userSessionId = crypto.randomUUID(); // Generate UUID for this session
    console.log(`User session ID: ${userSessionId}`);

    document.addEventListener('keydown', async (event) => {
        const key = event.key;
        console.log(`Key pressed: ${key}`);
        pressedKeyElement.textContent = key.toLowerCase();
        //toLowerCase b/c runes font has no upper case for some letters

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
              const protectedButton = document.getElementById('protected-link');
              if (protectedButton) {
                 protectedButton.style.display = 'block';
                 protectedButton.onclick = function() {
                    window.location.href = `/protected_resource?session_id=${userSessionId}`;
                 };
              }
            }
        } catch (error) {
            console.error('Error sending keypress event:', error);
        }
    });
});
