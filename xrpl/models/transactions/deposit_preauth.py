"""
Represents a DepositPreauth transaction on the XRP Ledger.

A DepositPreauth transaction gives another account pre-approval to deliver payments
to the sender of this transaction.

`See Deposit Authorization <https://xrpl.org/depositauth.html>`_
`See DepositPreauth <https://xrpl.org/depositauth.html>`_
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class DepositPreauth(Transaction):
    """
    Represents a DepositPreauth transaction on the XRP Ledger.

    A DepositPreauth transaction gives another account pre-approval to deliver payments
    to the sender of this transaction.

    `See Deposit Authorization <https://xrpl.org/depositauth.html>`_
    `See DepositPreauth <https://xrpl.org/depositauth.html>`_
    """

    authorize: Optional[str] = None
    unauthorize: Optional[str] = None
    transaction_type: TransactionType = field(
        default=TransactionType.DEPOSIT_PREAUTH,
        init=False,
    )

    def _get_errors(self: DepositPreauth) -> Dict[str, str]:
        errors = super()._get_errors()
        if self.authorize and self.unauthorize:
            errors[
                "DepositPreauth"
            ] = "One of authorize and unauthorize must be set, not both."

        if not self.authorize and not self.unauthorize:
            errors["DepositPreauth"] = "One of authorize and unauthorize must be set."

        return errors
