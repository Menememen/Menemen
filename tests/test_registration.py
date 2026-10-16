import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Testlerden önce veri tabanını oluşturmak ve testlerden sonra temizlemek için kullanılan test düzeneği."""
    create_db()
    yield
    try:
        if os.path.exists('users.db'):
            os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Test sırasında veri tabanı bağlantısı oluşturur ve testten sonra bağlantıyı kapatır."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Veri tabanı ve 'users' tablosunun oluşturulmasını test eder."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "'users' tablosu veri tabanında bulunmalıdır."


def test_add_new_user(setup_database, connection):
    """Yeni bir kullanıcının eklenmesini test eder."""
    result = add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert result is True, "Kullanıcı başarıyla eklendiğinde True dönmelidir."
    assert user, "Kullanıcı veri tabanına eklenmiş olmalıdır."


def test_add_existing_user(setup_database):
    """Var olan bir kullanıcı adıyla tekrar kullanıcı eklemeye çalışmayı test eder."""
    result = add_user('testuser', 'different@example.com', 'newpassword')
    assert result is False, "Aynı kullanıcı adı tekrar eklenmeye çalışıldığında False dönmelidir."


def test_authenticate_user_success(setup_database):
    """Başarılı kullanıcı doğrulamasını test eder."""
    assert authenticate_user('testuser', 'password123') is True, "Doğru kullanıcı adı ve şifre ile True dönmelidir."


def test_authenticate_user_nonexistent(setup_database):
    """Var olmayan bir kullanıcıyla doğrulama yapmayı test eder."""
    assert authenticate_user('nonexistent_user', 'password123') is False, "Var olmayan kullanıcı için False dönmelidir."


def test_authenticate_user_wrong_password(setup_database):
    """Yanlış şifreyle doğrulama yapmayı test eder."""
    assert authenticate_user('testuser', 'wrongpassword') is False, "Yanlış şifre için False dönmelidir."


def test_display_users(setup_database, capsys):
    """Kullanıcı listesinin doğru şekilde görüntülenmesini test eder."""
    display_users()
    captured = capsys.readouterr()
    assert "testuser" in captured.out, "Ekrana basılan kullanıcı listesinde 'testuser' yer almalıdır."