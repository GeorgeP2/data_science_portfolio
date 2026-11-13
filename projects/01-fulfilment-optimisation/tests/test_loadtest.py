import datetime as dt

import numpy as np
import pandas as pd
from fulfilment_optimisation.loadtest import Credentials, request_mix, sign, summarise

from portfolio import ProjectPaths, load_config

CFG = load_config(ProjectPaths.from_file(__file__).config)


def test_sigv4_matches_aws_test_suite():
    # "get-vanilla" from the AWS Signature Version 4 test suite.
    creds = Credentials("AKIDEXAMPLE", "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY")
    headers = sign(
        "GET",
        "https://example.amazonaws.com/",
        b"",
        creds,
        region="us-east-1",
        service="service",
        now=dt.datetime(2015, 8, 30, 12, 36, tzinfo=dt.UTC),
    )
    assert headers["authorization"] == (
        "AWS4-HMAC-SHA256 Credential=AKIDEXAMPLE/20150830/us-east-1/service/aws4_request, "
        "SignedHeaders=host;x-amz-date, "
        "Signature=5fa00fa31553b73ebf1942676e86291e8372ff2a2260956d9b8aae1d763fbf31"
    )


def test_session_token_is_signed():
    creds = Credentials("AKID", "secret", token="tok")
    headers = sign("POST", "https://x.lambda-url.eu-west-2.on.aws/batch", b"{}", creds, "eu-west-2")
    assert headers["x-amz-security-token"] == "tok"
    assert "x-amz-security-token" in headers["authorization"]


def test_request_mix_uses_development_seeds_and_valid_bodies():
    from fulfilment_optimisation.api.schemas import BatchRequest

    lt = {**CFG.loadtest, "scenarios": ["baseline"], "seeds": [0, 0]}
    bodies = request_mix(lt, CFG.generator)
    assert len(bodies) > 1
    for body in bodies:
        BatchRequest.model_validate(body)
        assert len(body["orders"]) <= CFG.api.max_orders


def test_summarise_excludes_warmup_and_counts_throttles():
    rows = [
        {"concurrency": 1, "warmup": True, "sent_at": 0.0, "status_code": 200,
         "client_ms": 9000.0, "server_ms": 900.0, "fallback_used": False},
        {"concurrency": 1, "warmup": False, "sent_at": 1.0, "status_code": 429,
         "client_ms": 5.0, "server_ms": np.nan, "fallback_used": None},
    ] + [
        {"concurrency": 1, "warmup": False, "sent_at": 2.0 + i, "status_code": 200,
         "client_ms": 100.0 + i, "server_ms": 90.0 + i, "fallback_used": False}
        for i in range(10)
    ]  # fmt: skip
    summary = summarise(pd.DataFrame(rows)).iloc[0]
    assert summary.requests == 11
    assert summary.throttled == 1
    assert summary.ok == 10
    assert summary.client_max == 109.0  # the warm-up request's 9 s isn't counted
