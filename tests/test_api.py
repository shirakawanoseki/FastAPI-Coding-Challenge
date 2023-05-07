
def test_create_user(test_db, client):
    response = client.post(
        "/users/",
        json={"email": "deadpool@example.com"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "deadpool@example.com"
    assert "id" in data
    assert "password" in data
    user_id = data["id"]
    password = data["password"]

    headers = {'x_api_token': password}
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "deadpool@example.com"
    assert data["id"] == user_id


def test_me_items(test_db, client):
    # ユーザーを作成する
    response = client.post(
        "/users/",
        json={"email": "deadpool@example.com"},
    )
    data = response.json()
    user_id = data["id"]
    password = data["password"]

    # ヘッダー
    headers = {'x_api_token': password}

    # ユーザーにアイテムを付与する(1つ目)。
    response = client.post(
        f"/users/{user_id}/items/",
        headers=headers,
        json={"title": "Title of test item 001",
              "description": "Description of test item 001"},
    )
    data_item_001 = response.json()
    id_item_001 = data_item_001["id"]

    # ユーザーにアイテムを付与する(２つ目)。
    response = client.post(
        f"/users/{user_id}/items/",
        headers=headers,
        json={"title": "Title of test item 002",
              "description": "Description of test item 002"},
    )
    data_item_002 = response.json()
    id_item_002 = data_item_002["id"]

    # ユーザーに付与したアイテムを取得して確認
    response = client.get(f"/me/items/{user_id}", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json() == (
        [
            {
                "title": "Title of test item 001",
                "description": "Description of test item 001",
                "id": id_item_001,
                "owner_id": user_id
            },
            {
                "title": "Title of test item 002",
                "description": "Description of test item 002",
                "id": id_item_002,
                "owner_id": user_id
            }
        ]

    )


def test_delete_user(test_db, client):

    # アイテムが譲渡されるユーザーを作成しておく
    response = client.post(
        "/users/",
        json={"email": "deadpool@example.com"},
    )
    granted_user_data = response.json()
    granted_user_id = granted_user_data["id"]

    # 削除の対象になるユーザーを作成する
    response = client.post(
        "/users/",
        json={"email": "catcat@example.com"},
    )
    data = response.json()
    user_id = data["id"]
    password = data["password"]

    # ヘッダー
    headers = {'x_api_token': password}

    # ユーザーにアイテムを付与する(1つ目)。
    response = client.post(
        f"/users/{user_id}/items/",
        headers=headers,
        json={"title": "Title of test item 001",
              "description": "Description of test item 001"},
    )
    data_item_001 = response.json()
    id_item_001 = data_item_001["id"]

    # ユーザーにアイテムを付与する(２つ目)。
    response = client.post(
        f"/users/{user_id}/items/",
        headers=headers,
        json={"title": "Title of test item 002",
              "description": "Description of test item 002"},
    )
    data_item_002 = response.json()
    id_item_002 = data_item_002["id"]

    # レスポンスのチェック
    headers = {'x_api_token': password}
    response = client.get(f"/users/delete/{user_id}", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json() == (
        {
            "email": "deadpool@example.com",
            "id": granted_user_id,
            "is_active": 1,
            "items": [
                {
                    "title": "Title of test item 001",
                    "description": "Description of test item 001",
                    "id": id_item_001,
                    "owner_id": granted_user_id
                },
                {
                    "title": "Title of test item 002",
                    "description": "Description of test item 002",
                    "id": id_item_002,
                    "owner_id": granted_user_id
                }
            ]
        }

    )
