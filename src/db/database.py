import mysql.connector
from mysql.connector import Error

class DatabaseConnection:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        try:
            self._connection = mysql.connector.connect(
                host='localhost',
                database='attendance_system',
                user='root',
                password=''
            )
            print("Kết nối MySQL thành công!")
        except Error as e:
            print(f"Lỗi kết nối MySQL: {e}")

    def get_connection(self):
        if not self._connection.is_connected():
            self._connect()
        return self._connection

    def _close(self):
        self._connection.close()


def test_connection() -> bool:
    try:
        db = DatabaseConnection()
        connection = db.get_connection()
        if connection.is_connected():
            print("Kết nối MySQL đang hoạt động.")
            return True
        else:
            print("Kết nối MySQL không hoạt động.")
            return False
    except Exception as e:
        print(f"Lỗi khi kiểm tra kết nối: {e}")
        return False


if __name__ == "__main__":
    test_connection()
