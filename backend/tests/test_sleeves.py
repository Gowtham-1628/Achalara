"""Tests for sleeves and multi-level (sleeve/account/client) roll-ups."""

from tests.conftest import create_test_client_and_account


def _strategy(client, name):
    return client.post(
        "/api/v1/strategies/", json={"name": name, "description": ""}
    ).json()["id"]


def _sleeve(client, client_id, account_id, strategy_id):
    return client.post(
        f"/api/v1/clients/{client_id}/accounts/{account_id}/sleeves",
        json={"strategy_id": strategy_id},
    )


def _buy(client, sleeve_id, symbol, qty, price, trade_date="2024-01-15"):
    resp = client.post(
        "/api/v1/trades/",
        json={
            "sleeve_id": sleeve_id,
            "trade_date": trade_date,
            "symbol": symbol,
            "action": "BUY",
            "quantity": qty,
            "price": price,
            "commission": 0,
        },
    )
    assert resp.status_code == 201


class TestSleeveCRUD:
    def test_create_and_get_sleeve(self, client):
        client_id, account_id = create_test_client_and_account(
            client, client_email="sl_crud@test.com"
        )
        strat_id = _strategy(client, "Growth")

        resp = _sleeve(client, client_id, account_id, strat_id)
        assert resp.status_code == 201
        data = resp.json()
        assert data["strategy_id"] == strat_id
        assert data["strategy_name"] == "Growth"
        sleeve_id = data["id"]

        got = client.get(
            f"/api/v1/clients/{client_id}/accounts/{account_id}/sleeves/{sleeve_id}"
        )
        assert got.status_code == 200
        assert got.json()["id"] == sleeve_id

    def test_duplicate_sleeve_conflict(self, client):
        client_id, account_id = create_test_client_and_account(
            client, client_email="sl_dup@test.com"
        )
        strat_id = _strategy(client, "Growth")

        assert _sleeve(client, client_id, account_id, strat_id).status_code == 201
        # Same strategy in same account again -> 409
        assert _sleeve(client, client_id, account_id, strat_id).status_code == 409

    def test_same_strategy_across_two_accounts(self, client):
        """One global strategy can run in two different accounts (two sleeves)."""
        client_id, account_a = create_test_client_and_account(
            client, client_email="sl_multi@test.com", account_name="Account A"
        )
        account_b = client.post(
            f"/api/v1/clients/{client_id}/accounts",
            json={"name": "Account B", "description": ""},
        ).json()["id"]
        strat_id = _strategy(client, "Growth")

        assert _sleeve(client, client_id, account_a, strat_id).status_code == 201
        assert _sleeve(client, client_id, account_b, strat_id).status_code == 201

    def test_create_sleeve_unknown_strategy(self, client):
        client_id, account_id = create_test_client_and_account(
            client, client_email="sl_nostrat@test.com"
        )
        resp = _sleeve(client, client_id, account_id, "nope")
        assert resp.status_code == 404


class TestRollUps:
    def test_account_merges_sleeves(self, client):
        """Account-level positions/performance merge across its sleeves."""
        client_id, account_id = create_test_client_and_account(
            client, client_email="rollup_acct@test.com"
        )
        s1 = _sleeve(client, client_id, account_id, _strategy(client, "Growth")).json()[
            "id"
        ]
        s2 = _sleeve(client, client_id, account_id, _strategy(client, "Income")).json()[
            "id"
        ]

        _buy(client, s1, "AAPL", 100, 100.0)  # cost 10000
        _buy(client, s2, "MSFT", 50, 200.0)  # cost 10000

        # Account positions = union of both sleeves
        pos = client.get(
            f"/api/v1/clients/{client_id}/accounts/{account_id}/positions"
        ).json()
        assert pos["positions_count"] == 2
        assert {p["symbol"] for p in pos["positions"]} == {"AAPL", "MSFT"}
        assert pos["total_cost_basis"] == 20000.0

        # Account performance counts trades across both sleeves and exposes children
        perf = client.get(
            f"/api/v1/clients/{client_id}/accounts/{account_id}/performance"
        ).json()
        assert perf["level"] == "account"
        assert perf["summary"]["trades_count"] == 2
        assert perf["summary"]["total_cost_basis"] == 20000.0
        assert len(perf["children"]) == 2

    def test_client_merges_accounts(self, client):
        """Client-level roll-up merges across accounts and their sleeves."""
        client_id, account_a = create_test_client_and_account(
            client, client_email="rollup_client@test.com", account_name="A"
        )
        account_b = client.post(
            f"/api/v1/clients/{client_id}/accounts",
            json={"name": "B", "description": ""},
        ).json()["id"]

        growth = _strategy(client, "Growth")
        sa = _sleeve(client, client_id, account_a, growth).json()["id"]
        sb = _sleeve(client, client_id, account_b, growth).json()["id"]

        _buy(client, sa, "AAPL", 10, 100.0)  # cost 1000
        _buy(client, sb, "AAPL", 5, 100.0)  # cost 500

        perf = client.get(f"/api/v1/clients/{client_id}/performance").json()
        assert perf["level"] == "client"
        assert perf["summary"]["trades_count"] == 2
        assert perf["summary"]["total_cost_basis"] == 1500.0
        # one child per account
        assert len(perf["children"]) == 2

        # Client positions merge the same symbol across both accounts
        pos = client.get(f"/api/v1/clients/{client_id}/positions").json()
        aapl = next(p for p in pos["positions"] if p["symbol"] == "AAPL")
        assert aapl["quantity"] == 15.0
