"""High-level encrypted field for Odoo models."""

import struct
from operator import attrgetter
from typing import Any

import psycopg2
from cryptography.fernet import Fernet, InvalidToken

from odoo.fields import Field
from odoo.tools import config
from odoo.tools.translate import _

_BINARY = memoryview


class Encrypted(Field):
    """
    Encapsulate an encrypted field in Odoo models.

    This field is designed to store sensitive data in an encrypted form in the database.

    :ivar string: The name of the field in the model
    :ivar required: Whether the field is required.
    :ivar readonly: Whether the field is read-only.
    :ivar help: A help message for the field.
    :ivar index: Whether to index the field.
    :ivar default: A default value for the field.
    """

    type = "encrypted"
    column_type = ("bytea", "bytea")  # Use bytea to store binary data in PostgreSQL
    value_type = None

    # pylint: disable=W8110
    def _setup_attrs(self, model_class, name):
        super()._setup_attrs(model_class, name)
        self._validate_value_type(self.value_type)

    _description_value_type = property(attrgetter("value_type"))

    @classmethod
    def _get_cipher(cls) -> Fernet:
        """
        Get encryption cipher using the environment key.

        :return: The encryption cipher.
        :raises ValueError: If the encryption key is not found in the config.
        """
        env = config.get("running_env", "prod")
        if not (key_str := config.get(f"encryption_key_{env}")):
            key_str = config.get("encryption_key")
        if not key_str:
            raise ValueError("No encryption key found in the config.")
        return Fernet(key_str.encode())

    @staticmethod
    def _validate_value_type(value_type: str) -> None:
        """
        Validate the value type.

        :param value_type: The type of the value.
        """
        if not value_type:
            raise ValueError(_("No value type specified for encrypted field!"))
        if value_type not in ("str", "int", "float", "bool"):
            raise ValueError(
                _("Unknown type indicator! Supported types are str, int, bool and float.")
            )

    @staticmethod
    def _to_bytes(value: str | int | float | bool, value_type: str) -> bytes:
        """
        Convert a value to bytes, prefixing with type information.

        :param value: The value to convert.
        :param value_type: The type of the value.

        :return: The converted value.
        :raises ValueError: If the type indicator is unknown.
        """
        Encrypted._validate_value_type(value_type)
        try:
            if value_type == "str":
                return value.encode()
            if value_type == "int":
                # Convert numbers to string and then to bytes for simplicity
                return str(value).encode()
            if value_type == "float":
                # Convert float to a high-precision string and then to bytes
                high_precision_str = format(value, ".17g")  # Adjust precision if needed
                return high_precision_str.encode()
            if value_type == "bool":
                return (1 if value else 0).to_bytes(1)
        except AttributeError as e:
            raise ValueError(
                _("The value might not be compatible with the type. %s") % str(e)
            ) from e
        except (TypeError, struct.error) as e:
            raise ValueError(
                _("This error may indicate an unsupported type or format issue. %s") % str(e)
            ) from e
        except Exception as e:
            raise ValueError(_("Unexpected error during value conversion: %s") % str(e)) from e

    @staticmethod
    def _from_bytes(byte_data: bytes, value_type: str) -> str | int | float | bool:
        """
        Convert bytes back to the original type, using prefixed type information.

        :param byte_data: The byte data to convert.
        :param value_type: The type of the value.

        :return: The converted value.
        :raises ValueError: If the type indicator is unknown.
        """
        try:
            if value_type == "str":
                return byte_data.decode()
            if value_type == "int":
                return int(byte_data.decode())
            if value_type == "float":
                return float(byte_data.decode())
            if value_type == "bool":
                return bool(int.from_bytes(byte_data))
        except UnicodeDecodeError as e:
            raise ValueError(_("Failed to decode byte data.")) from e
        except ValueError as e:
            raise ValueError(_(f"Failed to convert byte data to {value_type}: {e}")) from e

    def _decrypt_value(self, value):
        """
        Decrypt the value and convert it to the appropriate type.

        The ``value`` may be a memoryview.
        """
        cipher = self._get_cipher()
        try:
            decrypted_value = cipher.decrypt(value)
            return self._from_bytes(decrypted_value, self.value_type)
        except InvalidToken as e:
            raise ValueError(_("Invalid encryption key or corrupted data.")) from e

    def convert_to_column(self, value: Any, record, values: dict = None, validate: bool = True):
        """
        Convert ``value`` from the ``write`` format to the SQL format.

        :param value: The value to convert.
        :param record: The record containing the field.
        :param values: The values to write to the database.
        :param validate: Whether to validate the value.

        :return: The converted value.
        :raises ValueError: If the encryption key is invalid or the data is corrupted.
        """
        if not value:
            return None

        self._validate_value_type(self.value_type)
        value = self._to_bytes(value, self.value_type)
        cipher = self._get_cipher()

        try:
            encrypted_value = cipher.encrypt(value)
        except InvalidToken as e:
            raise ValueError(_("Invalid encryption key or corrupted data.")) from e

        result = psycopg2.Binary(encrypted_value)
        return result

    def convert_to_cache(self, value, record, validate=True):
        """
        Convert ``value`` to the cache format.

        The ``value`` may come from an assignment, or have the format of methods
        :meth:`BaseModel.read` or :meth:`BaseModel.write`.

        :param value:
        :param record:
        :param bool validate: when True, field-specific validation of ``value``
            will be performed
        """
        if isinstance(value, _BINARY):
            return self._decrypt_value(value)
        if isinstance(value, str):
            # the cache must contain bytes or memoryview, but sometimes a string
            # is given when assigning a binary field (test `TestFileSeparator`)
            return value
        return None if value is False else value

    def convert_to_record(self, value, record):
        """
        Convert ``value`` from the cache format to the record format.

        The ``value`` may come from cache
        """
        if isinstance(value, _BINARY):
            return self._decrypt_value(bytes(value))
        return False if value is None else value
