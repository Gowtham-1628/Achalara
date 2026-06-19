"""Tests for trade validators"""

from app.services.trade_ingestion import TradeValidator


class TestTradeValidator:
    """Test trade validation"""

    def test_valid_trade_row(self):
        """Test validating a valid trade row"""
        validator = TradeValidator()
        row = {
            "Date": "2026-01-15",
            "Symbol": "AAPL",
            "Action": "BUY",
            "Quantity": "100",
            "Price": "150.50",
            "Commission": "10.00",
            "Strategy": "Growth",
            "Notes": "Test trade",
        }

        is_valid, trade = validator.validate_row(row, 2)
        assert is_valid is True
        assert trade.symbol == "AAPL"
        assert trade.quantity == 100.0

    def test_invalid_quantity(self):
        """Test validation with invalid quantity"""
        validator = TradeValidator()
        row = {
            "Date": "2026-01-15",
            "Symbol": "AAPL",
            "Action": "BUY",
            "Quantity": "-100",  # Invalid: negative
            "Price": "150.50",
            "Commission": "0",
            "Strategy": "Growth",
        }

        is_valid, trade = validator.validate_row(row, 2)
        assert is_valid is False

    def test_invalid_date_format(self):
        """Test validation with invalid date format"""
        validator = TradeValidator()
        row = {
            "Date": "01/15/2026",  # Invalid format
            "Symbol": "AAPL",
            "Action": "BUY",
            "Quantity": "100",
            "Price": "150.50",
            "Commission": "0",
            "Strategy": "Growth",
        }

        is_valid, trade = validator.validate_row(row, 2)
        assert is_valid is False

    def test_batch_validation(self):
        """Test validating batch of trades"""
        validator = TradeValidator()
        rows = [
            {
                "Date": "2026-01-15",
                "Symbol": "AAPL",
                "Action": "BUY",
                "Quantity": "100",
                "Price": "150.50",
                "Commission": "10",
                "Strategy": "Growth",
            },
            {
                "Date": "2026-01-20",
                "Symbol": "MSFT",
                "Action": "SELL",
                "Quantity": "50",
                "Price": "300",
                "Commission": "5",
                "Strategy": "Growth",
            },
        ]

        result = validator.validate_batch(rows)
        assert result["total"] == 2
        assert result["valid"] == 2
        assert result["invalid"] == 0
