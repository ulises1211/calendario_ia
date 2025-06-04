import os
import main

# ensure we start with a clean slate
if os.path.exists(main.DB_FILE):
    os.remove(main.DB_FILE)
main.init_db()

def test_create_validate():
    appt = main.Appointment(id=1, name="Test", date="2025-06-01", time="10:00", service="consulta", yape_code="abc")
    main.save_appointment(appt)
    loaded = main.load_appointments()
    assert len(loaded) == 1
    assert loaded[0].name == "Test"

    res = main.validate_payment(1, "abc")
    assert res.confirmed is True

    appts = main.load_appointments()
    assert appts[0].confirmed is True


def test_user_registration_and_login():
    user_in = main.UserCreate(username="alice", password="secret", name="Alice", whatsapp="12345")
    user = main.register_user(user_in)
    assert user.id == 1
    users = main.get_users()
    assert len(users) == 1
    assert users[0].username == "alice"
    creds = main.Credentials(username="alice", password="secret")
    logged = main.login(creds)
    assert logged.id == 1
