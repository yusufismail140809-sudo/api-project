def _register_and_login(client, email="budi@mail.com", password="rahasia123"):
    """Helper: register + login, balikin token & ID."""
    register_response = client.post("/auth/register", json={
        "name": "Budi", "email": email, "password": password
    })
    # Ambil ID dari response register
    # (Tapi response register kamu belum balikin ID, jadi kita ambil dari /me aja)
    
    login_response = client.post("/auth/login", data={
        "username": email, "password": password
    })
    token = login_response.json()["access_token"]
    
    # Ambil data user buat dapet ID
    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    user_id = me_response.json()["id"]
    
    return token, user_id


def test_get_users(client):
    """Test ambil daftar user (pagination)."""
    token, _ = _register_and_login(client)
    response = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total_records"] == 1
    assert len(data["data"]) == 1


def test_create_user_admin_style(client):
    """Test bikin user baru tanpa password (POST /users)."""
    token, _ = _register_and_login(client)
    response = client.post("/users", json={
        "name": "Ani", "email": "ani@mail.com"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["name"] == "Ani"


def test_get_user_by_id(client):
    token, user_id = _register_and_login(client)
    response = client.get(f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "budi@mail.com"


def test_get_user_tidak_ada(client):
    """Test ambil user yang gak ada (ID 999)."""
    token, _ = _register_and_login(client)
    response = client.get("/users/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_delete_diri_sendiri(client):
    token, user_id = _register_and_login(client)
    response = client.delete(f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_delete_orang_lain_403(client):
    """Test hapus akun orang lain (harus ditolak 403)."""
    # Budi login (dapet token Budi)
    token_budi, _ = _register_and_login(client, email="budi@mail.com")
    
    # Ani register & login (dapet token Ani & ID Ani)
    _, ani_id = _register_and_login(client, email="ani@mail.com", password="rahasia456")
    
    # Budi coba hapus Ani
    response = client.delete(
        f"/users/{ani_id}", 
        headers={"Authorization": f"Bearer {token_budi}"}
    )
    assert response.status_code == 403
    assert "Gak boleh hapus user lain" in response.json()["detail"]


def test_delete_tanpa_token(client):
    """Test hapus user tanpa token (harus 401)."""
    response = client.delete("/users/1")
    assert response.status_code == 401