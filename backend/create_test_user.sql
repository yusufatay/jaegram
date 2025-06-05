-- Test user için gerekli tabloları oluştur
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    email TEXT UNIQUE,
    email_verified INTEGER DEFAULT 0,
    full_name TEXT,
    profile_pic_url TEXT,
    coin_balance INTEGER DEFAULT 0,
    is_admin INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    is_admin_platform INTEGER DEFAULT 0,
    instagram_pk TEXT UNIQUE,
    instagram_username TEXT,
    instagram_session_data TEXT
);

-- Test kullanıcısını ekle
INSERT OR REPLACE INTO users (
    username,
    password_hash,
    email,
    email_verified,
    full_name,
    profile_pic_url,
    coin_balance,
    is_admin,
    is_active,
    is_admin_platform,
    instagram_pk,
    instagram_username,
    instagram_session_data
) VALUES (
    'testuser',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBAQHxqKJxqKJx',  -- 'testpassword123' şifresinin hash'i
    'testuser@example.com',
    1,
    'Test User',
    'https://via.placeholder.com/150',
    5000,
    0,
    1,
    0,
    '12345678901',
    'test_instagram_user',
    '{"session_id": "mock_session", "csrf_token": "mock_csrf", "user_id": "12345678901"}'
); 