from app.broker_connectors.kotak.kotak_connector import KotakNeoConnector
from app.models.models import TradingJournal

def test_list_trades_empty(client, auth_headers):
    response = client.get("/api/v1/trading/journal", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_log_trade_success(client, auth_headers):
    payload = {
        "ticker": "RELIANCE",
        "type": "Long",
        "quantity": 10,
        "entry_price": 2400.0,
        "strategy": "Breakout",
        "psychology_notes": "Felt calm and structured."
    }
    response = client.post("/api/v1/trading/journal", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["ticker"] == "RELIANCE"
    assert data["pnl"] == 0.0

def test_exit_trade_long_pnl_calculation(client, auth_headers, db, test_user):
    trade = TradingJournal(
        user_id=test_user.id,
        ticker="TCS",
        type="Long",
        quantity=5,
        entry_price=3000.0,
        pnl=0.0
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)

    payload = {
        "exit_price": 3100.0,
        "psychology_notes": "Exited at resistance target."
    }
    response = client.put(f"/api/v1/trading/journal/{trade.id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    # PnL for Long: (3100 - 3000) * 5 * 1 = 500.0
    assert data["pnl"] == 500.0
    assert data["exit_price"] == 3100.0

def test_exit_trade_short_pnl_calculation(client, auth_headers, db, test_user):
    trade = TradingJournal(
        user_id=test_user.id,
        ticker="INFY",
        type="Short",
        quantity=10,
        entry_price=1500.0,
        pnl=0.0
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)

    payload = {
        "exit_price": 1450.0
    }
    response = client.put(f"/api/v1/trading/journal/{trade.id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    # PnL for Short: (1450 - 1500) * 10 * (-1) = -50 * 10 * -1 = 500.0
    assert data["pnl"] == 500.0

def test_broker_connectors():
    from app.broker_connectors.fyers.fyers_connector import FyersConnector
    # Test Fyers connector simulation paths
    fyers = FyersConnector()
    assert fyers.establish_session("dummy_code") is True
    order_res = fyers.place_order("SBIN", 50, 600.0, "BUY")
    assert order_res["status"] == "Success"
    assert order_res["order_id"] == "FYERS_54321"

    # Test Kotak connector simulation paths
    kotak = KotakNeoConnector()
    assert kotak.establish_session({"token": "dummy_credentials"}) is True
    # Kotak connector file has simulation fallback as well
