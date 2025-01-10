from ack.helpers import run_reword


def test_gpt():
    prompt = "This is a test. Please include 'test' in your response."

    message = run_reword(prompt)

    assert message is not None
    assert "test" in message
