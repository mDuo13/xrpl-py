"""Model for NFTokenAcceptOffer transaction type."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from xrpl.models.amounts import Amount, get_amount_value
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTokenAcceptOffer(Transaction):
    """
    The NFTokenOfferAccept transaction is used to accept offers
    to buy or sell an NFToken. It can either:

    1. Allow one offer to be accepted. This is called direct
       mode.
    2. Allow two distinct offers, one offering to buy a
       given NFToken and the other offering to sell the same
       NFToken, to be accepted in an atomic fashion. This is
       called brokered mode.

    To indicate direct mode, use either the `sell_offer` or
    `buy_offer` fields, but not both. To indicate brokered mode,
    use both the `sell_offer` and `buy_offer` fields. If you use
    neither `sell_offer` nor `buy_offer`, the transaction is invalid.
    """

    sell_offer: Optional[str] = None
    """
    Identifies the NFTokenOffer that offers to sell the NFToken.

    In direct mode this field is optional, but either SellOffer or
    BuyOffer must be specified. In brokered mode, both SellOffer
    and BuyOffer must be specified.
    """

    buy_offer: Optional[str] = None
    """
    Identifies the NFTokenOffer that offers to buy the NFToken.

    In direct mode this field is optional, but either SellOffer or
    BuyOffer must be specified. In brokered mode, both SellOffer
    and BuyOffer must be specified.
    """

    broker_fee: Optional[Amount] = None
    """
    This field is only valid in brokered mode. It specifies the
    amount that the broker will keep as part of their fee for
    bringing the two offers together; the remaining amount will
    be sent to the seller of the NFToken being bought. If
    specified, the fee must be such that, prior to accounting
    for the transfer fee charged by the issuer, the amount that
    the seller would receive is at least as much as the amount
    indicated in the sell offer.

    This functionality is intended to allow the owner of an
    NFToken to offer their token for sale to a third party
    broker, who may then attempt to sell the NFToken on for a
    larger amount, without the broker having to own the NFToken
    or custody funds.

    Note: in brokered mode, the offers referenced by BuyOffer
    and SellOffer must both specify the same TokenID; that is,
    both must be for the same NFToken.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.NFTOKEN_ACCEPT_OFFER,
        init=False,
    )

    def _get_errors(self: NFTokenAcceptOffer) -> Dict[str, str]:
        return {
            key: value
            for key, value in {
                **super()._get_errors(),
                "sell_offer": self._get_sell_offer_error(),
                "buy_offer": self._get_buy_offer_error(),
                "broker_fee": self._get_broker_fee_error(),
            }.items()
            if value is not None
        }

    def _get_sell_offer_error(self: NFTokenAcceptOffer) -> Optional[str]:
        if self.broker_fee is not None and self.sell_offer is None:
            return "Must be set if using brokered mode"
        if self.sell_offer is None and self.buy_offer is None:
            return "Must set either buy_offer or sell_offer"
        return None

    def _get_buy_offer_error(self: NFTokenAcceptOffer) -> Optional[str]:
        if self.broker_fee is not None and self.buy_offer is None:
            return "Must be set if using brokered mode"
        if self.sell_offer is None and self.buy_offer is None:
            return "Must set either buy_offer or sell_offer"
        return None

    def _get_broker_fee_error(self: NFTokenAcceptOffer) -> Optional[str]:
        if self.broker_fee is not None and get_amount_value(self.broker_fee) <= 0:
            return "Must be greater than 0; omit if there is no broker fee"
        return None
