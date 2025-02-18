"""
Represents a CheckCancel transaction on the XRP ledger. A CheckCancel
transaction cancels an unredeemed Check, removing it from the ledger
without sending any money. The source or the destination of the check
can cancel a Check at any time using this transaction type. If the
Check has expired, any address can cancel it.

`See CheckCancel <https://xrpl.org/checkcancel.html>`_
"""
from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class CheckCancel(Transaction):
    """
    Represents a CheckCancel transaction on the XRP ledger. A CheckCancel
    transaction cancels an unredeemed Check, removing it from the ledger
    without sending any money. The source or the destination of the check
    can cancel a Check at any time using this transaction type. If the
    Check has expired, any address can cancel it.

    `See CheckCancel <https://xrpl.org/checkcancel.html>`_
    """

    #: This field is required.
    check_id: str = REQUIRED  # type: ignore
    transaction_type: TransactionType = field(
        default=TransactionType.CHECK_CANCEL,
        init=False,
    )
