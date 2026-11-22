def test_register_sukses(client):
    """Test register user baru."""
    response = client.post("/auth/register", json={
        "name": "Budi",
        "email": "budi@mail.com",
        "password": "rahasia123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Registrasi berhasil"
    assert "kode" in data


def test_register_email_dobel(client):
    """Test register dengan email yang udah terdaftar."""
    # Register pertama
    client.post("/auth/register", json={
        "name": "Budi",
        "email": "budi@mail.com",
        "password": "rahasia123"
    })
    
    # Register kedua dengan email sama
    response = client.post("/auth/register", json={
        "name": "Ani",
        "email": "budi@mail.com",
        "password": "rahasia456"
    })
    assert response.status_code == 400
    assert "sudah terdaftar" in response.json()["detail"]


def test_register_password_pendek(client):
    """Test register dengan password kurang dari 6 huruf."""
    response = client.post("/auth/register", json={
        "name": "Budi",
        "email": "budi@mail.com",
        "password": "123"
    })
    assert response.status_code == 422  # Pydantic validation error


def test_login_sukses(client):
    """Test login pake kredensial yang bener."""
    # Register dulu
    client.post("/auth/register", json={
        "name": "Budi",
        "email": "budi@mail.com",
        "password": "rahasia123"
    })
    
    # Login
    response = client.post("/auth/login", data={
        "username": "budi@mail.com",
        "password": "rahasia123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_password_salah(client):
    """Test login pake password yang salah."""
    # Register
    client.post("/auth/register", json={
        "name": "Budi",
        "email": "budi@mail.com",
        "password": "rahasia123"
    })
    
    # Login pake password salah
    response = client.post("/auth/login", data={
        "username": "budi@mail.com",
        "password": "salah456"
    })
    assert response.status_code == 401
    assert "Kredensial tidak valid" in response.json()["detail"]


def test_me_tanpa_token(client):
    """Test akses endpoint /auth/me tanpa token."""
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_dengan_token(client):
    """Test akses endpoint /auth/me dengan token yang valid."""
    # Register & Login
    client.post("/auth/register", json={
        "name": "Budi",
        "email": "budi@mail.com",
        "password": "rahasia123"
    })
    login_response = client.post("/auth/login", data={
        "username": "budi@mail.com",
        "password": "rahasia123"
    })
    token = login_response.json()["access_token"]
    
    # Akses /me pakai token
    response = client.get("/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "budi@mail.com"
    assert data["name"] == "Budi"
    assert "password_hash" not in data  # Jangan bocorin hash