import jwt
import pytest

from models.user import User
from services.authentication_serivce import AuthenticationService, JWT_ALGORITHM, AuthenticationError


def test_encode(mock_user: User):
    secret = "test_secret"

    token = AuthenticationService.generate_token(
        sub=mock_user.id,
        secret=secret
    )

    decoded_token = jwt.decode(
        token,
        secret,
        JWT_ALGORITHM
    )

    assert decoded_token.get("sub") == mock_user.id


def test_decode():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            ".eyJpc3MiOiJhdXRoZW50aWNhdGlvbl9zZXJ" \
            "2aWNlIiwic3ViIjoxMjM0NTY3ODkwLCJpYXQ" \
            "iOjE3MTE2NzExMDAsImV4cCI6MjAwMDAwMDA" \
            "wMDB9" \
            ".ZI3oZpKDUSqWeYYnG7UXfNsdEc9W9Mq9M4x" \
            "DWQmyXyE"
    sub = 1234567890

    decoded_token = AuthenticationService.decode_token(token, secret)
    assert sub == decoded_token.get("sub")


def test_decode_invalid_signature():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            ".eyJpc3MiOiJtZXRhZGF0YV9zZXJ2aWNlIiw" \
            "ic3ViIjoxMjM0NTY3ODkwLCJpYXQiOjE3MTE" \
            "2NzExMDAsImV4cCI6MjAwMDAwMDAwMDB9" \
            ".HXHmIoegomXWsgWOVGlh-QmIzu_Hld68LywdCD7AjCZ"

    with pytest.raises(AuthenticationError):
        AuthenticationService.decode_token(token, secret)


def test_decode_invalid_exp():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            ".eyJpc3MiOiJtZXRhZGF0YV9zZXJ2aWNlIiw" \
            "ic3ViIjoxMjM0NTY3ODkwLCJpYXQiOjE3MTE" \
            "2NzExMDAsImV4cCI6MH0" \
            ".VdcY5GZkIT2MLPPRZ_ECtTed9m_LbeA5x0Jit_WS5Os"

    with pytest.raises(AuthenticationError):
        AuthenticationService.decode_token(token, secret)


def test_decode_missing_exp():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            ".eyJpc3MiOiJtZXRhZGF0YV9zZXJ2aWNlIiw" \
            "ic3ViIjoxMjM0NTY3ODkwLCJpYXQiOjE3MTE" \
            "2NzExMDB9" \
            ".ZGcqMyiTpKY9A2yjQ4XTokiLXKDmKIQYZmqEp-Ce-8I"

    with pytest.raises(AuthenticationError):
        AuthenticationService.decode_token(token, secret)


def test_decode_invalid_iss():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            ".eyJzdWIiOjEyMzQ1Njc4OTAsImlhdCI6MTc" \
            "xMTY3MTEwMCwiZXhwIjoyMDAwMDAwMDAwMH0" \
            ".N3L45Fx4LrhqzdgO5TMYaDkmU-OKHYDUjUDU36wHXug"

    with pytest.raises(AuthenticationError):
        AuthenticationService.decode_token(token, secret)


def test_decode_missing_iss():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            ".eyJpc3MiOiJ3cm9uZ19pc3MiLCJzdWIiOjE" \
            "yMzQ1Njc4OTAsImlhdCI6MTcxMTY3MTEwMCw" \
            "iZXhwIjoyMDAwMDAwMDAwMH0" \
            ".1VF2pRozuF0p7bRN7aU5Ed4MPYOADnrkxbqCWM9_L9Y"

    with pytest.raises(AuthenticationError):
        AuthenticationService.decode_token(token, secret)


def test_decode_invalid_format():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            "eyJzdWIiOjEyMzQ1Njc4OTAsIm5hbWUiOiJK" \
            "b2huIERvZSIsImlhdCI6MTUxNjIzOTAyMn0" \
            "xQ6rmPEgPsYj8n4XICbLSw_CuOQ6FqVqFNL" \
            "HTQbdQhY"

    with pytest.raises(AuthenticationError):
        AuthenticationService.decode_token(token, secret)


def test_decode_no_sub():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            ".eyJuYW1lIjoiSm9obiBEb2UiLCJpYXQiOjE1MTYyMzkwMjJ9" \
            ".nfxWdUayk54niAULlEOjvac-fUdltdWIYY1sg1Yd5Ts"

    with pytest.raises(AuthenticationError):
        AuthenticationService.decode_token(token, secret)
