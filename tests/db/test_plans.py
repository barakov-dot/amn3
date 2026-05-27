from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema


def test_seed_default_plans_creates_day_based_tariffs(tmp_path):
    repo = _repo(tmp_path)

    repo.seed_default_plans()
    repo.seed_default_plans()

    plans = repo.list_active_plans()
    assert [plan["duration_days"] for plan in plans] == [3, 7, 10, 14, 30, 60, 90, 180]
    assert plans[1]["id"] == "days_7"
    assert plans[1]["name"] == "7 days"
    assert plans[1]["price"] == 0
    assert plans[1]["currency"] == "RUB"


def test_create_order_stores_selected_plan_id(tmp_path):
    repo = _repo(tmp_path)
    repo.seed_default_plans()
    user_id = repo.upsert_user(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
    )

    order_id = repo.create_order(
        user_id=user_id,
        plan_id="days_30",
        payment_mode="free_test",
    )

    order = repo.get_order(order_id)
    assert order["plan_id"] == "days_30"
    assert repo.get_plan("days_30")["duration_days"] == 30


def _repo(tmp_path):
    conn = connect(tmp_path / "plans.sqlite3")
    initialize_schema(conn)
    return Repository(conn)
