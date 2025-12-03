import mysql.connector

def get_connection():
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="inventory_system"
    )
    return con


def create_db():
    """Tạo database và các bảng nếu chưa có."""
    con = get_connection()
    cur = con.cursor()

    # Bảng employee
    cur.execute("""
        CREATE TABLE IF NOT EXISTS employee(
            eid INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100),
            email VARCHAR(100),
            gender VARCHAR(10),
            contact VARCHAR(20),
            dob VARCHAR(20),
            doj VARCHAR(20),
            pass VARCHAR(100),
            utype VARCHAR(20),
            address TEXT,
            salary VARCHAR(20)
        )
    """)

    # Bảng supplier
    cur.execute("""
        CREATE TABLE IF NOT EXISTS supplier(
            invoice INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100),
            contact VARCHAR(20),
            `desc` TEXT
        )
    """)

    # Bảng category
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category(
            cid INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100)
        )
    """)

    # Bảng product
    cur.execute("""
        CREATE TABLE IF NOT EXISTS product(
            pid INT PRIMARY KEY AUTO_INCREMENT,
            Category VARCHAR(100),
            Supplier VARCHAR(100),
            name VARCHAR(100),
            price VARCHAR(20),
            qty VARCHAR(20),
            status VARCHAR(20)
        )
    """)

    con.commit()
    con.close()
    print("Database and tables are ready.")
