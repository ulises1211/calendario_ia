import os
import json
import main

# ensure we start with a clean slate
if os.path.exists(main.DATA_FILE):
    os.remove(main.DATA_FILE)

def test_create_validate():
    appt = main.Appointment(id=1, name="Test", date="2025-06-01", time="10:00", yape_code="abc")
    main.save_appointments([appt])
    loaded = main.load_appointments()
    assert len(loaded) == 1
    assert loaded[0].name == "Test"

    res = main.validate_payment(1, "abc")
    assert res.confirmed is True

    appts = main.load_appointments()
    assert appts[0].confirmed is True
