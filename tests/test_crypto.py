"""Tests for backend crypto module."""

from hexenapi.backend.crypto import (
    b64_decode,
    b64_encode,
    build_canonical_string,
    generate_x_client_token,
    generate_x_tr_signature,
    md5_hex,
)


def test_md5_hex():
    assert md5_hex(b"hello") == "5d41402abc4b2a76b9719d911017c592"
    assert md5_hex(b"") == "d41d8cd98f00b204e9800998ecf8427e"


def test_b64_encode_decode_roundtrip():
    data = b"test data 123"
    encoded = b64_encode(data)
    assert isinstance(encoded, str)
    decoded = b64_decode(encoded)
    assert decoded == data


def test_b64_decode_padding():
    # "a" encodes to "YQ==" — test with missing padding
    assert b64_decode("YQ") == b"a"
    assert b64_decode("YQ=") == b"a"
    assert b64_decode("YQ==") == b"a"


def test_generate_x_client_token():
    token = generate_x_client_token(timestamp_ms=1234567890000)
    parts = token.split(",")
    assert len(parts) == 2
    assert parts[0] == "1234567890000"
    # Second part should be md5 of reversed timestamp
    assert parts[1] == md5_hex(b"0000987654321")

def test_generate_x_client_token_no_args():
    token = generate_x_client_token()
    token = generate_x_client_token()
    parts = token.split(",")
    assert len(parts) == 2
    assert len(parts[0]) == 13  # ms timestamp is 13 digits
    assert len(parts[1]) == 32  # md5 hex is 32 chars


def test_build_canonical_string():
    canon = build_canonical_string(
        method="GET",
        accept="application/json",
        content_type="application/json",
        url="https://example.com/path?b=2&a=1",
        body=None,
        timestamp_ms=12345,
    )
    lines = canon.split("\n")
    assert lines[0] == "GET"
    assert lines[1] == "application/json"
    assert lines[2] == "application/json"
    assert lines[3] == ""  # no body length
    assert lines[4] == "12345"
    assert lines[5] == ""  # no body hash
    # Query keys should be sorted
    assert "a=1&b=2" in lines[6]


def test_build_canonical_string_with_body():
    canon = build_canonical_string(
        method="POST",
        accept="*/*",
        content_type="text/plain",
        url="https://example.com/api",
        body="hello",
        timestamp_ms=99,
    )
    lines = canon.split("\n")
    assert lines[0] == "POST"
    assert lines[3] == "5"  # len("hello")
    assert lines[4] == "99"
    assert lines[5] == md5_hex(b"hello")


def test_generate_x_tr_signature():
    sig = generate_x_tr_signature(
        method="GET",
        accept="application/json",
        content_type="application/json",
        url="https://example.com/test",
        timestamp_ms=12345,
    )
    parts = sig.split("|")
    assert len(parts) == 3
    assert parts[0] == "12345"
    assert parts[1] == "2"
    # Third part should be base64-encoded signature
    assert len(parts[2]) > 0


def test_generate_x_tr_signature_deterministic():
    kwargs = dict(
        method="GET",
        accept="application/json",
        content_type="application/json",
        url="https://example.com/test",
        timestamp_ms=12345,
    )
    sig1 = generate_x_tr_signature(**kwargs)
    sig2 = generate_x_tr_signature(**kwargs)
    assert sig1 == sig2
