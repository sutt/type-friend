import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class KeyBufferManager:
    """
    Manages user-specific keypress buffers and checks for a secret spell sequence.
    """

    def __init__(self, parsed_secret_spell: List[str]):
        """
        Initializes the KeyBufferManager with the secret spell.
        """
        self._user_key_buffers: Dict[str, List[str]] = {}
        self._parsed_secret_spell: List[str] = parsed_secret_spell
        self._spell_key_count: int = len(parsed_secret_spell)
        logger.info(
            f"KeyBufferManager initialized with spell: {self._parsed_secret_spell} "
        )

    def add_key(self, user_uuid: str, key: str) -> List[str]:
        """
        Adds a key to the buffer for a specific user and trims the buffer.

        The buffer is trimmed to the length of the secret spell. If the spell
        length is zero, the buffer will be emptied.
        """
        current_buffer = self._user_key_buffers.get(user_uuid, [])
        current_buffer.append(key)

        if self._spell_key_count > 0:
            current_buffer = current_buffer[-self._spell_key_count :]
        elif self._spell_key_count == 0:
            current_buffer = []

        self._user_key_buffers[user_uuid] = current_buffer
        logger.debug(
            f"Buffer for UUID {user_uuid} updated. Key '{key}' added. New buffer: {current_buffer}"
        )
        return current_buffer

    def get_buffer(self, user_uuid: str) -> List[str]:
        """
        Retrieves the current key buffer for a specific user.
        """
        return self._user_key_buffers.get(user_uuid, [])

    def check_spell(self, user_uuid: str) -> bool:
        """
        Checks if the buffer for a user [case-insenstive] matches the secret spell.
        """
        if not self._parsed_secret_spell:
            return False

        current_buffer = self.get_buffer(user_uuid)
        logger.debug(
            f"Checking spell for UUID {user_uuid}. Original Buffer: {current_buffer}, Original Spell: {self._parsed_secret_spell}"
        )

        buffer_lower = [key.lower() for key in current_buffer]
        spell_lower = [key.lower() for key in self._parsed_secret_spell]
        return buffer_lower == spell_lower
