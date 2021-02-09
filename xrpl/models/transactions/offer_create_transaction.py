"""TODO: docstring"""
from __future__ import annotations  # Requires Python 3.7+

from typing import Any, Dict, List, Optional, Union

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.issued_currency import IssuedCurrency
from xrpl.models.transactions.transaction import Transaction


class OfferCreateTransaction(Transaction):
    """
    Represents an OfferCreate transaction on the XRP Ledger.
    An OfferCreate transaction is effectively a limit order.
    It defines an intent to exchange currencies, and creates
    an Offer object if not completely fulfilled when placed.
    Offers can be partially fulfilled.

    See https://xrpl.org/offercreate.html.
    """

    def __init__(
        self: OfferCreateTransaction,
        *,
        account: str,
        fee: str,
        sequence: int,
        taker_gets: Union[str, IssuedCurrency],
        taker_pays: Union[str, IssuedCurrency],
        expiration: Optional[int] = None,
        offer_sequence: Optional[int] = None,
        account_transaction_id: Optional[str] = None,
        flags: Optional[int] = None,
        last_ledger_sequence: Optional[int] = None,
        memos: Optional[List[Any]] = None,
        signers: Optional[List[Any]] = None,
        source_tag: Optional[int] = None,
        signing_public_key: Optional[str] = None,
        transaction_signature: Optional[str] = None,
    ):
        """TODO: docstring"""
        self.taker_gets = taker_gets
        self.taker_pays = taker_pays
        self.expiration = expiration
        self.offer_sequence = offer_sequence
        super().__init__(
            account=account,
            transaction_type="OfferCreate",
            fee=fee,
            sequence=sequence,
            account_transaction_id=account_transaction_id,
            flags=flags,
            last_ledger_sequence=last_ledger_sequence,
            memos=memos,
            signers=signers,
            source_tag=source_tag,
            signing_public_key=signing_public_key,
            transaction_signature=transaction_signature,
        )

    @classmethod
    def from_dict(
        cls: OfferCreateTransaction, value: Dict[str, Any]
    ) -> OfferCreateTransaction:
        """TODO: docstring"""
        assert "taker_gets" in value
        assert "taker_pays" in value

        if isinstance(value["taker_gets"], str):
            taker_gets = value["taker_gets"]
        elif isinstance(value["taker_gets"], dict):
            taker_gets = IssuedCurrency.from_value(value["taker_gets"])
        else:
            raise XRPLModelException(
                "Cannot convert `taker_gets` value into `str` or `IssuedCurrency`"
            )

        if isinstance(value["taker_pays"], str):
            taker_pays = value["taker_pays"]
        elif isinstance(value["taker_pays"], dict):
            taker_pays = IssuedCurrency.from_value(value["taker_pays"])
        else:
            raise XRPLModelException(
                "Cannot convert `taker_pays` value into `str` or `IssuedCurrency`"
            )

        expiration = None
        if "expiration" in value:
            assert isinstance(
                value["expiration"], int
            ), "`expiration` value is not an integer"
            expiration = value["expiration"]

        offer_sequence = None
        if "offer_sequence" in value:
            assert isinstance(
                value["offer_sequence"], int
            ), "`offer_sequence` value is not an integer"
            offer_sequence = value["offer_sequence"]

        return OfferCreateTransaction(
            taker_gets=taker_gets,
            taker_pays=taker_pays,
            expiration=expiration,
            offer_sequence=offer_sequence,
        )

    def to_json(self) -> Dict[str, Any]:
        """TODO: docstring"""
        return_dict = {"taker_gets": self.taker_gets, "taker_pays": self.taker_pays}
        if self.expiration is not None:
            return_dict["expiration"] = self.expiration
        if self.offer_sequence is not None:
            return_dict["offer_sequence"] = self.offer_sequence

        return {**self._get_transaction_json(), **return_dict}
