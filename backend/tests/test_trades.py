"""Tests for trade endpoints"""

from tests.conftest import create_test_strategy


class TestTradeEndpoints:
    """Test trade API endpoints"""

    def get_sleeve_id(self, client):
        """Helper to create a strategy and return its ID"""
        _, _, sleeve_id = create_test_strategy(
            client,
            client_email="trade@test.com",
            strategy_name="Trade Test Strategy",
        )
        return sleeve_id

    def test_create_trade(self, client):
        """Test creating a trade"""
        sleeve_id = self.get_sleeve_id(client)

        response = client.post(
            "/api/v1/trades/",
            json={
                "sleeve_id": str(sleeve_id),
                "trade_date": "2026-05-15",
                "symbol": "AAPL",
                "action": "BUY",
                "quantity": 100,
                "price": 150.50,
                "commission": 10.00,
                "notes": "Initial purchase",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["action"] == "BUY"
        assert float(data["quantity"]) == 100
        assert float(data["price"]) == 150.50

    def test_create_trade_invalid_quantity(self, client):
        """Test creating trade with invalid quantity"""
        sleeve_id = self.get_sleeve_id(client)

        response = client.post(
            "/api/v1/trades/",
            json={
                "sleeve_id": str(sleeve_id),
                "trade_date": "2026-05-15",
                "symbol": "AAPL",
                "action": "BUY",
                "quantity": -100,
                "price": 150.50,
                "commission": 0,
            },
        )

        assert response.status_code == 422

    def test_create_trade_invalid_price(self, client):
        """Test creating trade with invalid price"""
        sleeve_id = self.get_sleeve_id(client)

        response = client.post(
            "/api/v1/trades/",
            json={
                "sleeve_id": str(sleeve_id),
                "trade_date": "2026-05-15",
                "symbol": "AAPL",
                "action": "BUY",
                "quantity": 100,
                "price": -150.50,
                "commission": 0,
            },
        )

        assert response.status_code == 422

    def test_create_trade_for_nonexistent_strategy(self, client):
        """Test creating trade for non-existent strategy"""
        response = client.post(
            "/api/v1/trades/",
            json={
                "sleeve_id": "00000000-0000-0000-0000-000000000000",
                "trade_date": "2026-05-15",
                "symbol": "AAPL",
                "action": "BUY",
                "quantity": 100,
                "price": 150.50,
                "commission": 0,
            },
        )

        assert response.status_code == 404

    def test_create_multiple_trades(self, client):
        """Test creating multiple trades for same strategy"""
        sleeve_id = self.get_sleeve_id(client)

        trades = [
            {
                "trade_date": "2026-01-15",
                "symbol": "AAPL",
                "action": "BUY",
                "quantity": 100,
                "price": 150.00,
                "commission": 10.00,
            },
            {
                "trade_date": "2026-02-15",
                "symbol": "MSFT",
                "action": "BUY",
                "quantity": 50,
                "price": 300.00,
                "commission": 5.00,
            },
            {
                "trade_date": "2026-03-15",
                "symbol": "AAPL",
                "action": "SELL",
                "quantity": 50,
                "price": 160.00,
                "commission": 10.00,
            },
        ]

        for trade_data in trades:
            response = client.post(
                "/api/v1/trades/", json={"sleeve_id": str(sleeve_id), **trade_data}
            )
            assert response.status_code == 201

    def test_create_trade_invalid_action(self, client):
        """Test creating trade with invalid action"""
        sleeve_id = self.get_sleeve_id(client)

        response = client.post(
            "/api/v1/trades/",
            json={
                "sleeve_id": str(sleeve_id),
                "trade_date": "2026-05-15",
                "symbol": "AAPL",
                "action": "INVALID",
                "quantity": 100,
                "price": 150.50,
                "commission": 0,
            },
        )

        assert response.status_code == 422
