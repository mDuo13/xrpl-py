"""
Represents a SignerListSet transaction on the XRP Ledger.

The SignerListSet transaction creates, replaces, or removes a list of signers that can
be used to multi-sign a transaction. This transaction type was introduced by the
MultiSign amendment.

`See SignerListSet <https://xrpl.org/signerlistset.html>`_
`See MultiSign Amendment <https://xrpl.org/known-amendments.html#multisign>`_
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from xrpl.models.base_model import BaseModel
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class SignerEntry(BaseModel):
    """
    Each member of the SignerEntries field is an object that describes that
    signer in the list.
    """

    #: This field is required.
    account: str = REQUIRED  # type: ignore
    #: This field is required.
    signer_weight: int = REQUIRED  # type: ignore

    @classmethod
    def is_dict_of_model(cls: Type[SignerEntry], dictionary: Dict[str, Any]) -> bool:
        """
        Returns True if the input dictionary was derived by the `to_dict`
        method of an instance of this class. In other words, True if this is
        a dictionary representation of an instance of this class.

        NOTE: does not account for model inheritance, IE will only return True
        if dictionary represents an instance of this class, but not if
        dictionary represents an instance of a subclass of this class.

        Args:
            dictionary: The dictionary to check.

        Returns:
            True if dictionary is a dict representation of an instance of this
            class.
        """
        return (
            isinstance(dictionary, dict)
            and "signer_entry" in dictionary
            and super().is_dict_of_model(dictionary["signer_entry"])
        )

    def to_dict(self: SignerEntry) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a SignerEntry.

        Returns:
            The dictionary representation of a BaseModel.
        """
        return {"signer_entry": super().to_dict()}


@require_kwargs_on_init
@dataclass(frozen=True)
class SignerListSet(Transaction):
    """
    Represents a SignerListSet transaction on the XRP Ledger.

    The SignerListSet transaction creates, replaces, or removes a list of signers that
    can be used to multi-sign a transaction. This transaction type was introduced by the
    MultiSign amendment.

    `See SignerListSet <https://xrpl.org/signerlistset.html>`_
    `See MultiSign Amendment <https://xrpl.org/known-amendments.html#multisign>`_
    """

    #: This field is required.
    signer_quorum: int = REQUIRED  # type: ignore
    signer_entries: Optional[List[SignerEntry]] = None
    transaction_type: TransactionType = field(
        default=TransactionType.SIGNER_LIST_SET,
        init=False,
    )

    def _get_errors(self: SignerListSet) -> Dict[str, str]:
        errors = super()._get_errors()

        # deleting a signer list requires self.signer_quorum == 0 and
        # self.signer_entries is None
        if self.signer_quorum == 0 and self.signer_entries is not None:
            errors["signer_list_set"] = (
                "Must not include a `signer_entries` value if the signer list is being "
                "deleted."
            )
        if self.signer_quorum != 0 and self.signer_entries is None:
            errors["signer_list_set"] = (
                "Must have a value of zero for `signer_quorum` if the signer list is "
                "being deleted."
            )

        if self.signer_entries is None:  # deletion of the SignerList object
            return errors

        if self.signer_quorum <= 0:
            errors[
                "signer_quorum"
            ] = "`signer_quorum` must be greater than or equal to 0."

        if len(self.signer_entries) < 1 or len(self.signer_entries) > 8:
            errors["signer_entries"] = (
                "`signer_entries` must have at least 1 member and no more than 8 "
                "members. If this transaction is deleting the SignerList, then "
                "this parameter must be omitted."
            )
            return errors

        account_set = set()
        signer_weight_sum = 0

        for signer_entry in self.signer_entries:
            if signer_entry.account == self.account:
                errors["signer_entries"] = (
                    "The account submitting the transaction cannot appear in a "
                    "signer entry."
                )
            account_set.add(signer_entry.account)
            signer_weight_sum += signer_entry.signer_weight

        if self.signer_quorum > signer_weight_sum:
            errors["signer_quorum"] = (
                "`signer_quorum` must be less than or equal to the sum of the "
                "SignerWeight values in the `signer_entries` list."
            )

        if len(account_set) != len(self.signer_entries):
            errors["signer_entries"] = (
                "An account cannot appear multiple times in the list of signer "
                "entries."
            )
        return errors
