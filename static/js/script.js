document.addEventListener('DOMContentLoaded', () => {
    const pressedKeyElement = document.getElementById('pressed-key');

    document.addEventListener('keydown', async (event) => {
        const key = event.key;
        console.log(`Key pressed: ${key}`);
        pressedKeyElement.textContent = key;

        try {
            const response = await fetch('/keypress', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ key: key }),
            });

            if (!response.ok) {
                console.error('Failed to send keypress event to server:', response.statusText);
                return;
            }

            const result = await response.json();
            console.log('Server response:', result);
        } catch (error) {
            console.error('Error sending keypress event:', error);
        }
    });
});
