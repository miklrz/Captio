import random
import string

import pytest

from conftest import auth_headers


FUZZ_STRINGS = [
    "",
    " ",
    "\t\n",
    "\x00",
    "' OR 1=1 --",
    "<script>alert(1)</script>",
    "../etc/passwd",
    "😀" * 32,
    "a" * 512,
]


def generated_strings(count: int = 16) -> list[str]:
    rng = random.Random(20260622)
    alphabet = string.ascii_letters + string.digits + " _-.'<>/\\\n\t"
    return [
        "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 160)))
        for _ in range(count)
    ]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"name": None, "login": None, "password": None},
        *(
            {"name": value, "login": value, "password": value}
            for value in [*FUZZ_STRINGS, *generated_strings()]
        ),
        {"name": "Valid", "login": "valid", "password": "123"},
        {"name": "Valid", "login": "valid", "password": "x" * 250},
        {"name": ["array"], "login": {"object": True}, "password": 123456},
    ],
)
def test_register_fuzz_rejects_bad_payloads_without_500(test_client, payload):
    response = test_client.post("/api/auth/register", json=payload)

    assert response.status_code < 500
    assert response.status_code in {201, 409, 422}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        *(
            {"login": value, "password": value}
            for value in [*FUZZ_STRINGS, *generated_strings()]
        ),
    ],
)
def test_login_fuzz_never_returns_500(test_client, payload):
    response = test_client.post("/api/auth/login", json=payload)

    assert response.status_code < 500
    assert response.status_code in {401, 404, 422}


@pytest.mark.parametrize("role", ["", "admin ", "user\n", "moderator", "root", 123, None])
def test_role_update_fuzz_validates_role_values(test_client, role):
    user_response = test_client.post(
        "/api/auth/register",
        json={"name": "Role Target", "login": f"role-target-{role!r}", "password": "secure123"},
    )
    assert user_response.status_code == 201
    user_id = user_response.json()["user"]["id"]

    response = test_client.patch(
        f"/api/auth/users/{user_id}/role",
        headers=auth_headers(test_client),
        json={"role": role},
    )

    assert response.status_code < 500
    assert response.status_code == 422


@pytest.mark.parametrize("title", [*FUZZ_STRINGS, *generated_strings(), [], {}, None])
def test_task_title_fuzz_never_returns_500(test_client, title):
    response = test_client.post(
        "/api/tasks/",
        headers=auth_headers(test_client, "paimon", "123456"),
        json={"title": title},
    )

    assert response.status_code < 500
    assert response.status_code in {201, 422}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        *(
            {
                "video_url": value,
                "task": "transcribe",
                "language": None,
                "target_language": "en",
            }
            for value in [*FUZZ_STRINGS, *generated_strings()]
        ),
        {"video_url": "ftp://example.com/video.mp4", "task": "transcribe"},
        {"video_url": "https://example.com/video.mp4", "task": "delete"},
        {"video_url": "https://example.com/video.mp4", "task": "translate", "target_language": "klingon"},
        {"video_url": "https://example.com/video.mp4", "source_type": "database"},
    ],
)
def test_video_request_fuzz_rejects_invalid_json_without_500(test_client, payload):
    response = test_client.post("/api/videos", json=payload)

    assert response.status_code < 500
    assert response.status_code == 422


@pytest.mark.parametrize(
    ("filename", "content", "form", "expected"),
    [
        ("payload.exe", b"not-video", {"task": "transcribe"}, 400),
        ("empty.mp4", b"", {"task": "transcribe"}, 400),
        ("sample.mp4", b"x", {"task": "translate", "target_language": "klingon"}, 422),
    ],
)
def test_upload_fuzz_rejects_invalid_files_without_500(test_client, filename, content, form, expected):
    response = test_client.post(
        "/api/videos/upload",
        files={"file": (filename, content, "application/octet-stream")},
        data=form,
    )

    assert response.status_code < 500
    assert response.status_code == expected


@pytest.mark.parametrize("token", ["", "bad", "Bearer", "Bearer bad.token.value", "Basic abc"])
def test_auth_header_fuzz_rejects_invalid_tokens_without_500(test_client, token):
    headers = {"Authorization": token} if token else {}
    response = test_client.get("/api/tasks/", headers=headers)

    assert response.status_code < 500
    assert response.status_code == 401
