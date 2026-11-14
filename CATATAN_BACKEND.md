# Catatan Belajar Backend

## 1. Struktur Project

- `config.py`: Baca file `.env` (DATABASE_URL, SECRET_KEY, dll).
- `security.py`: Hash password (bcrypt) & bikin JWT token.
- `databasebackend.py`: Buka/tutup koneksi database PostgreSQL pake `get_db()`.
- `repositories.py`: Query SQL (SELECT, INSERT, UPDATE, DELETE).
- `services.py`: Aturan bisnis (cek email dobel, validasi, dll).
- `schemas.py`: Validasi data (Pydantic).
- `deps.py`: Satpam (cek token JWT).
- `auth.py`: Endpoint register, login, me.
- `mainbackend.py`: Endpoint CRUD user.
- `main.py`: Gabungin semua router.

## 2. Alur Request

### Register (`POST /auth/register`)
1. `auth.py` terima request.
2. `schemas.py` validasi (name min 3 huruf, email valid, password min 6).
3. `services.py` cek email dobel.
4. `security.py` hash password.
5. `repositories.py` simpan ke database.
6. `databasebackend.py` commit (simpan permanen).

### Login (`POST /auth/login`)
1. `auth.py` terima request (form-urlencoded).
2. `services.py` cari user by email.
3. `security.py` verify password.
4. `security.py` bikin JWT token.
5. Balikin token ke user.

### Lihat Profil (`GET /auth/me`)
1. `deps.py` (satpam) cek token valid gak.
2. Kalau valid, ambil data user.
3. Balikin data user (tanpa password_hash).

## 3. Konsep Penting

### `@contextmanager` + `yield` di `get_db()`
- Otomatis commit kalau sukses.
- Otomatis rollback kalau error.
- Otomatis close koneksi (apapun yang terjadi).

### `TypeVar` & `Generic[T]`
- Bikin class/fungsi fleksibel.
- `PageResponse[T]` = cetakan response yang bisa diisi tipe apa aja.

### `Depends` (Dependency Injection)
- `Depends(get_current_user)` = panggil satpam dulu sebelum masuk.
- `Depends()` (tanpa argumen) = biar FastAPI bikin objek otomatis.

### `response_model`
- Ngecek bentuk output.
- Nyaring data sensitif.
- Dokumentasi Swagger lebih jelas.

## 4. Database

- **PostgreSQL**: Database production. Pake `psycopg2`.
- **SQLite**: Database lokal (belum buat production).
- **Commit**: Simpan permanen.
- **Rollback**: Batalkan semua perubahan.

## 5. Git (Penting!)

- `git add .`: Masukin file ke staging.
- `git commit -m "pesan"`: Simpen di lokal.
- `git push`: Kirim ke GitHub.

**JANGAN COMMIT `.env`!** Isinya password. Pake `.gitignore`.

## 6. Testing (Belum Dipelajari)

- `pytest`: Framework testing.
- `TestClient`: Test endpoint tanpa jalanin server.

## 7. Docker (Gagal Install)

- Windows 10 Enterprise LTSC 21H2 gak support Docker Desktop 4.97.
- PostgreSQL lokal jadi solusi.

## 8. UserResponse (Opsional, Belum Dibuat)

**Kenapa butuh UserResponse?**
- `GET /users/{id}` saat ini balikin dict mentah dari database.
- Ini **bisa bocorin** `password_hash` (meski udah di-hash, tetep gak boleh keliatan).
- `UserResponse` adalah cetakan (Pydantic) buat **nyaring data sensitif** biar gak ikut kebalikin.

**Kapan dibuat?**
- Nanti, pas project udah mau dipake orang beneran (production).
- Untuk belajar, gak wajib.

**Cara bikinnya (kalau nanti mau):**

1. Di `schemas.py`, tambahin:
```python
class UserResponse(BaseModel):
    id: int
    kode: str
    name: str
    email: str
    role: str
    # password_hash GAK dimasukin biar aman