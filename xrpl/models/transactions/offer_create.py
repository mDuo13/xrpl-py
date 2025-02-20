"""
Represents an OfferCreate transaction on the XRP Ledger. An OfferCreate transaction is
effectively a limit order. It defines an intent to exchange currencies, and creates an
Offer object if not completely fulfilled when placed. Offers can be partially fulfilled.

`See OfferCreate <https://xrpl.org/offercreate.html>`_
"""
from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class OfferCreate(Transaction):
    """
    Represents an OfferCreate transaction on the XRP Ledger. An OfferCreate
    transaction is effectively a limit order. It defines an intent to exchange
    currencies, and creates an Offer object if not completely fulfilled when
    placed. Offers can be partially fulfilled.

    `See OfferCreate <https://xrpl.org/offercreate.html>`_
    """

    #: This field is required.
    taker_gets: Amount = REQUIRED  # type: ignore
    #: This field is required.
    taker_pays: Amount = REQUIRED  # type: ignore
    expiration: Optional[int] = None
    offer_sequence: Optional[int] = None
    transaction_type: TransactionType = field(
        default=TransactionType.OFFER_CREATE,
        init=False,
    )
