from core.sms import SMS


def test_sms(capsys):
    SMS("01234567890", "hello world").send()
    assert "01234567890" in capsys.readouterr().out
