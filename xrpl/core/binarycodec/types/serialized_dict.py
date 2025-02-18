"""Class for serializing/deserializing Dicts of objects."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, Union

from typing_extensions import Final

from xrpl.core.addresscodec import is_valid_xaddress, xaddress_to_classic_address
from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.definitions import (
    FieldInstance,
    get_field_instance,
    get_ledger_entry_type_code,
    get_ledger_entry_type_name,
    get_transaction_result_code,
    get_transaction_result_name,
    get_transaction_type_code,
    get_transaction_type_name,
)
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.serialized_type import SerializedType

_OBJECT_END_MARKER_BYTE: Final[bytes] = bytes([0xE1])
_OBJECT_END_MARKER: Final[str] = "ObjectEndMarker"
_SERIALIZED_DICT: Final[str] = "SerializedDict"
_DESTINATION: Final[str] = "Destination"
_ACCOUNT: Final[str] = "Account"
_SOURCE_TAG: Final[str] = "SourceTag"
_DEST_TAG: Final[str] = "DestinationTag"


def _handle_xaddress(field: str, xaddress: str) -> Dict[str, Union[str, int]]:
    """Break down an X-Address into a classic address and a tag.

    Args:
        field: Name of field
        xaddress: X-Address corresponding to the field

    Returns:
        A dictionary representing the classic address and tag.

    Raises:
        XRPLBinaryCodecException: field-tag combo is invalid.
    """
    (classic_address, tag, is_test_network) = xaddress_to_classic_address(xaddress)
    if field == _DESTINATION:
        tag_name = _DEST_TAG
    elif field == _ACCOUNT:
        tag_name = _SOURCE_TAG
    elif tag is not None:
        raise XRPLBinaryCodecException(f"{field} cannot have an associated tag")

    if tag is not None:
        return {field: classic_address, tag_name: tag}
    return {field: classic_address}


def _str_to_enum(field: str, value: Any) -> Any:
    # all of these fields have enum values that are used for serialization
    # converts the string name to the corresponding enum code
    if field == "TransactionType":
        return get_transaction_type_code(value)
    if field == "TransactionResult":
        return get_transaction_result_code(value)
    if field == "LedgerEntryType":
        return get_ledger_entry_type_code(value)
    return value


def _enum_to_str(field: str, value: Any) -> Any:
    # reverse of the above function
    if field == "TransactionType":
        return get_transaction_type_name(value)
    if field == "TransactionResult":
        return get_transaction_result_name(value)
    if field == "LedgerEntryType":
        return get_ledger_entry_type_name(value)
    return value


class SerializedDict(SerializedType):
    """Class for serializing/deserializing Dicts of objects."""

    @classmethod
    def from_parser(
        cls: Type[SerializedDict],
        parser: BinaryParser,
        _length_hint: Optional[None] = None,
    ) -> SerializedDict:
        """
        Construct a SerializedDict from a BinaryParser.

        Args:
            parser: The parser to construct a SerializedDict from.

        Returns:
            The SerializedDict constructed from parser.
        """
        from xrpl.core.binarycodec.binary_wrappers.binary_serializer import (
            BinarySerializer,
        )

        serializer = BinarySerializer()

        while not parser.is_end():
            field = parser.read_field()
            if field.name == _OBJECT_END_MARKER:
                break

            associated_value = parser.read_field_value(field)
            serializer.write_field_and_value(field, associated_value)
            if field.type == _SERIALIZED_DICT:
                serializer.append(_OBJECT_END_MARKER_BYTE)

        return SerializedDict(bytes(serializer))

    @classmethod
    def from_value(
        cls: Type[SerializedDict], value: Dict[str, Any], only_signing: bool = False
    ) -> SerializedDict:
        """
        Create a SerializedDict object from a dictionary.

        Args:
            value: The dictionary to construct a SerializedDict from.
            only_signing: whether only the signing fields should be included.

        Returns:
            The SerializedDict object constructed from value.

        Raises:
            XRPLBinaryCodecException: If the SerializedDict can't be constructed
                from value.
        """
        from xrpl.core.binarycodec.binary_wrappers.binary_serializer import (
            BinarySerializer,
        )

        serializer = BinarySerializer()

        xaddress_decoded = {}
        for (k, v) in value.items():
            if isinstance(v, str) and is_valid_xaddress(v):
                handled = _handle_xaddress(k, v)
                if (
                    _SOURCE_TAG in handled
                    and handled[_SOURCE_TAG] is not None
                    and _SOURCE_TAG in value
                    and value[_SOURCE_TAG] is not None
                ):
                    raise XRPLBinaryCodecException(
                        "Cannot have Account X-Address and SourceTag"
                    )
                if (
                    _DEST_TAG in handled
                    and handled[_DEST_TAG] is not None
                    and _DEST_TAG in value
                    and value[_DEST_TAG] is not None
                ):
                    raise XRPLBinaryCodecException(
                        "Cannot have Destination X-Address and DestinationTag"
                    )
                xaddress_decoded.update(handled)
            else:
                xaddress_decoded[k] = _str_to_enum(k, v)

        sorted_keys: List[FieldInstance] = []
        for field_name in xaddress_decoded:
            field_instance = get_field_instance(field_name)
            if (
                field_instance is not None
                and xaddress_decoded[field_instance.name] is not None
                and field_instance.is_serialized
            ):
                sorted_keys.append(field_instance)
        sorted_keys.sort(key=lambda x: x.ordinal)

        if only_signing:
            sorted_keys = list(filter(lambda x: x.is_signing, sorted_keys))

        for field in sorted_keys:
            try:
                associated_value = field.associated_type.from_value(
                    xaddress_decoded[field.name]
                )
            except XRPLBinaryCodecException as e:
                # mildly hacky way to get more context in the error
                # provides the field name and not just the type it's expecting
                # keeps the original stack trace
                e.args = (f"Error processing {field.name}: {e.args[0]}",) + e.args[1:]
                raise
            serializer.write_field_and_value(field, associated_value)
            if field.type == _SERIALIZED_DICT:
                serializer.append(_OBJECT_END_MARKER_BYTE)

        return SerializedDict(bytes(serializer))

    def to_json(self: SerializedDict) -> Dict[str, Any]:
        """
        Returns the JSON representation of a SerializedDict.

        Returns:
            The JSON representation of a SerializedDict.
        """
        parser = BinaryParser(str(self))
        accumulator = {}

        while not parser.is_end():
            field = parser.read_field()
            if field.name == _OBJECT_END_MARKER:
                break
            json_value = parser.read_field_value(field).to_json()
            accumulator[field.name] = _enum_to_str(field.name, json_value)

        return accumulator
