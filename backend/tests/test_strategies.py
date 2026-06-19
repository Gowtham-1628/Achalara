"""Tests for global strategy definition endpoints"""


class TestStrategyDefinitionEndpoints:
    """Strategy definitions are firm-wide (global)."""

    def test_create_strategy(self, client):
        """Test creating a global strategy definition"""
        response = client.post(
            "/api/v1/strategies/",
            json={
                "name": "Growth Strategy",
                "description": "Aggressive growth approach",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Growth Strategy"
        assert data["description"] == "Aggressive growth approach"
        assert "id" in data

    def test_list_strategies(self, client):
        """Test listing global strategies"""
        for i in range(3):
            client.post(
                "/api/v1/strategies/",
                json={"name": f"Strategy {i + 1}", "description": f"Desc {i + 1}"},
            )

        response = client.get("/api/v1/strategies/")
        assert response.status_code == 200
        assert len(response.json()) >= 3

    def test_get_strategy(self, client):
        """Test fetching a single strategy"""
        created = client.post(
            "/api/v1/strategies/", json={"name": "Income", "description": "Yield"}
        ).json()

        response = client.get(f"/api/v1/strategies/{created['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == "Income"

    def test_get_nonexistent_strategy(self, client):
        """Fetching a missing strategy returns 404"""
        response = client.get("/api/v1/strategies/does-not-exist")
        assert response.status_code == 404

    def test_duplicate_name_case_insensitive(self, client):
        """Names are unique case-insensitively: 'growth' clashes with 'Growth'."""
        first = client.post(
            "/api/v1/strategies/", json={"name": "Growth", "description": ""}
        )
        assert first.status_code == 201

        dup = client.post(
            "/api/v1/strategies/", json={"name": "  growth ", "description": "x"}
        )
        assert dup.status_code == 409
