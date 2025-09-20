def test_export_import_roundtrip(client, db_session):
    resp = client.get("/agents/export")
    assert resp.status_code == 200
    pkg = resp.json()

    resp2 = client.post("/agents/import", json=pkg)
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["status"] == "ok"
    assert data["stats"]["created_agents"] >= 0