#!/bin/python

# Copyright 2024 Google LLC.
# SPDX-License-Identifier: Apache-2.0

# Standalone Python Script to control OBS with OBS Websockets
# -----------------------------------------------------------
# How to use -
#   Add shortcuts to this with args -
#     Alt+Shift+S '... --request ToggleStream'
#     Alt+F8 '... --request ToggleReplayBuffer'  # Activates replay for Alt+F10.
#     Alt+F10 '... --request SaveReplayBuffer'  # Same as NVidia instant replay.
# Status of OBS shortcuts -
#   With Wayland KDE as of 202408, the shortcuts set from OBS cannot work without focus.
#   As a workaround, we use websockets and this file set as shortcuts to control it.
# Status of OBS with websockets plugin -
#   OBS with websockets is now available on Arch official repo!
#   (Earlier, obs-studio-stable was the alternative that I used.)
# Status of python OBS websockets -
#   There are two repos: obsws and python-obs-websocket.
#   The first one is not available in AUR.
#   The second one is on AUR, but an old version which does not connect.
#   Hence I chose to do it from scratch using websockets directly.

import argparse
import base64
import functools
import hashlib
import json
import logging
import pathlib
import websocket  # Needs python-websocket-client

from typing import Any

# Generate or read the password from OBS Studio's Websocket Server Settings.
# Then put it in a file 'obs-password.txt' in the same directory as this script.
_OBS_PASSWORD_FILE = "obs-password.txt"

# This is incremented after each request.
_request_id = 0


@functools.cache
def _obs_password() -> str:
    with open(pathlib.Path(__file__).parent / _OBS_PASSWORD_FILE) as f:
        return f.read().strip()


def _build_auth_string(auth_resp: dict[str, str]) -> str:
    base64_secret = base64.b64encode(
        hashlib.sha256((_obs_password() + auth_resp["salt"]).encode("utf-8")).digest()
    ).decode("utf-8")
    auth = base64.b64encode(
        hashlib.sha256(
            (base64_secret + auth_resp["challenge"]).encode("utf-8")
        ).digest()
    ).decode("utf-8")
    return auth


def _connect_and_authenticate() -> websocket.WebSocket:
    obs_url = "ws://localhost:4455"

    ws = websocket.WebSocket()
    ws.connect(obs_url)

    # Receive initial message containing authentication challenge.
    response = json.loads(ws.recv())
    logging.info(response)
    auth = _build_auth_string(response["d"]["authentication"])
    logging.info(f"{auth=}")

    payload = {
        "op": 1,  # Identify
        "d": {"rpcVersion": 1, "authentication": auth, "eventSubscriptions": 1023},
    }
    ws.send(json.dumps(payload))
    response = ws.recv()
    logging.info(response)
    if not response:
        raise RuntimeError("Authentication failed.")

    return ws


def _send_request(
    ws: websocket.WebSocket, request_type: str
) -> tuple[bool, dict[str, Any]]:
    global _request_id
    request_id = f"obs-control-{_request_id}"
    _request_id += 1
    start_streaming_request = {
        "op": 6,  # Request
        "d": {
            "requestType": request_type,
            "requestId": request_id,
        },
    }
    ws.send(json.dumps(start_streaming_request))

    # Receive the response.
    response_str = ws.recv()
    logging.info(response_str)

    # The response has "d" and "op" (int) fields. We are interested in "d".
    response = json.loads(response_str)["d"]
    success = response["requestStatus"]["result"]
    result = response.get("responseData", {})
    return success, result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--request",
        required=True,
        help="Examples: StartStream, or ToggleStream. See requests documentation here: https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md",
    )

    args = parser.parse_args()
    ws = _connect_and_authenticate()
    _send_request(ws, args.request)
    ws.close()
    logging.info("Done.")


if __name__ == "__main__":
    main()
