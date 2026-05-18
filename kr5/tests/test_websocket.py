from starlette.websockets import WebSocketDisconnect


def test_connect_with_valid_username(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        event = websocket.receive_json()

    assert event == {"type": "joined", "room_id": "python", "username": "alice"}


def test_send_message_and_receive_broadcast(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()
        websocket.send_json({"type": "message", "text": "Всем привет"})
        event = websocket.receive_json()

    assert event == {
        "type": "message",
        "room_id": "python",
        "username": "alice",
        "text": "Всем привет",
    }


def test_two_clients_in_same_room_receive_same_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()
        with client.websocket_connect("/ws/rooms/python?username=bob") as bob:
            alice.receive_json()
            bob.receive_json()
            alice.send_json({"type": "message", "text": "hello"})
            message_for_alice = alice.receive_json()
            message_for_bob = bob.receive_json()

    expected = {
        "type": "message",
        "room_id": "python",
        "username": "alice",
        "text": "hello",
    }
    assert message_for_alice == expected
    assert message_for_bob == expected


def test_different_rooms_do_not_receive_foreign_messages(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as python_user:
        python_user.receive_json()
        with client.websocket_connect("/ws/rooms/java?username=bob") as java_user:
            java_user.receive_json()
            python_user.send_json({"type": "message", "text": "secret"})
            own_message = python_user.receive_json()

    assert own_message["room_id"] == "python"


def test_too_long_message_returns_error(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()
        websocket.send_json({"type": "message", "text": "x" * 301})
        event = websocket.receive_json()

    assert event == {"type": "error", "detail": "Message is too long"}


def test_disconnected_user_not_returned_in_room_users(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()
        response_inside = client.get("/rooms/python/users")

    response_after = client.get("/rooms/python/users")

    assert response_inside.json() == {"room_id": "python", "users": ["alice"]}
    assert response_after.json() == {"room_id": "python", "users": []}


def test_blank_username_closes_connection(client):
    try:
        with client.websocket_connect("/ws/rooms/python?username=   ") as websocket:
            websocket.receive_json()
    except WebSocketDisconnect as exc:
        assert exc.code == 1008
    else:
        raise AssertionError("Expected WebSocketDisconnect")
