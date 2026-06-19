"""Market price service for managing stock prices"""
from sqlalchemy.orm import Session  # noqa: F401
from decimal import Decimal
from typing import Dict, Optional
import logging


class MarketPrice:
    """In-memory market prices (can be extended to use external API)"""

    # In-memory override store (populated by manual update-market-prices endpoint)
    _prices: Dict[str, Decimal] = {}

    @classmethod
    def get_price(cls, symbol: str) -> Optional[Decimal]:
        """Get market price for a symbol"""
        return cls._prices.get(symbol.upper())

    @classmethod
    def set_price(cls, symbol: str, price: Decimal) -> None:
        """Set market price for a symbol"""
        cls._prices[symbol.upper()] = Decimal(str(price))

    @classmethod
    def get_all_prices(cls) -> Dict[str, Decimal]:
        """Get all market prices"""
        return cls._prices.copy()

    @classmethod
    def update_prices(cls, prices: Dict[str, Decimal]) -> None:
        """Update multiple prices at once"""
        for symbol, price in prices.items():
            cls.set_price(symbol, price)


class MarketPriceService:
    """Service for managing market prices"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_price(self, symbol: str) -> Optional[Decimal]:
        """Get market price for a symbol"""
        price = MarketPrice.get_price(symbol)
        self.logger.debug(f"Market price for {symbol}: {price}")
        return price

    def set_price(self, symbol: str, price: Decimal) -> None:
        """Set market price for a symbol"""
        MarketPrice.set_price(symbol, price)
        self.logger.info(f"Updated market price: {symbol} = {price}")

    def get_prices_for_symbols(self, symbols: list) -> Dict[str, Decimal]:
        """Get market prices for multiple symbols"""
        all_prices = MarketPrice.get_all_prices()
        return {s: all_prices[s] for s in symbols if s in all_prices}

    def update_prices_bulk(self, prices: Dict[str, Decimal]) -> Dict:
        """Update multiple prices at once"""
        updated = {}
        for symbol, price in prices.items():
            self.set_price(symbol, Decimal(str(price)))
            updated[symbol] = float(Decimal(str(price)))

        return {"status": "success", "updated": len(updated), "prices": updated}
