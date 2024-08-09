import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox


UserTxt = None
PassTxt = None
connection = None
cursor = None

def create_database_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="housepizza"
        )
        return connection
    except mysql.connector.Error as err:
        print("MySQL Hatası:", err)
        exit()

def create_tables(connection):
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT,
            pizza VARCHAR(50) NOT NULL,
            drink VARCHAR(50) NOT NULL,
            extras TEXT,
            total_price DECIMAL(10, 2),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)
    connection.commit()

def calculate_total_price(pizza_choice, drink_choice, extras_var):
    extras_choices = [extras_options[i] for i, var in enumerate(extras_var) if var.get()]

    pizza_price = get_product_price(pizza_choice)
    drink_price = get_product_price(drink_choice)
    extras_price = sum(get_product_price(extra) for extra in extras_choices)

    total_price = pizza_price + drink_price + extras_price

    return total_price

def place_order():
    customer_name = entry_name.get()
    pizza_choice = pizza_combo.get()
    drink_choice = drink_combo.get()
    extras_choices = [extras_options[i] for i, var in enumerate(extras_var) if var.get()]

    cursor.execute("INSERT INTO customers (name) VALUES (%s)", (customer_name,))
    connection.commit()

    cursor.execute("SELECT id FROM customers WHERE name = %s", (customer_name,))
    customer_id = cursor.fetchone()[0]

    total_price = calculate_total_price(pizza_choice, drink_choice, extras_var)

    cursor.execute("""
        INSERT INTO orders (customer_id, pizza, drink, extras, total_price)
        VALUES (%s, %s, %s, %s, %s)
    """, (customer_id, pizza_choice, drink_choice, ", ".join(extras_choices), total_price))
    connection.commit()

    messagebox.showinfo("Sipariş Alındı",
                        f"Sipariş Alınmıştır. Toplam Fiyat: {total_price} TL.")

def view_data():
    data_window = tk.Toplevel()
    data_window.title("Verileri Görüntüle")

    tree = ttk.Treeview(data_window)
    tree["columns"] = ("Müşteri ID", "Müşteri Adı", "Pizza", "İçecek", "Ekstralar", "Toplam Fiyat")

    tree.heading("#0", text="ID")
    tree.column("#0", width=50, anchor="center")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    cursor.execute("""
        SELECT customers.id AS customer_id, customers.name, orders.id, orders.pizza, orders.drink, orders.extras, orders.total_price
        FROM customers
        JOIN orders ON customers.id = orders.customer_id
    """)
    data = cursor.fetchall()

    for row in data:
        extras = row[5].split(", ") if row[5] else []
        extras_str = ", ".join(extras)
        tree.insert("", "end", values=(row[0], row[1], row[3], row[4], extras_str, row[6]))

    tree.pack(expand=True, fill="both")

def login_screen():
    global login_screen, UserTxt, PassTxt, connection, cursor

    login_screen = tk.Tk()
    login_screen.title("Giriş Ekranı")
    login_screen.geometry("310x200")
    login_screen.configure(background='#edd76b')

    Bannerlabel = tk.Label(login_screen, text="Giriş Yapınız", width=37, bg='white')
    Bannerlabel.place(x=20, y=20)

    UserLabel = tk.Label(login_screen, text="Kullanıcı Adı :", width=10, bg="#edd76b")
    UserLabel.place(x=20, y=60)

    UserTxt = tk.Entry(login_screen, width=27, relief="flat")
    UserTxt.place(x=120, y=60)

    UserTxt.focus()

    PassLabel = tk.Label(login_screen, text="Şifre :", width=10, bg="#edd76b")
    PassLabel.place(x=42, y=90)

    PassTxt = tk.Entry(login_screen, width=27, relief="flat", show="*")
    PassTxt.place(x=120, y=90)

    LoginBtn = tk.Button(login_screen, text="Giriş Yap", command=validate_login, relief="groove")
    LoginBtn.place(x=120, y=130)

    login_screen.mainloop()

def validate_login():
    global UserTxt, PassTxt, connection, cursor
    mydb = create_database_connection()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM login where usrname = '" + UserTxt.get() + "' and passwrd = '" + PassTxt.get() + "';")
    myresult = cursor.fetchone()
    mydb.close()

    if myresult is None:
        messagebox.showerror("Hata", "Kullanıcı Adı ve Şifre Yanlış")
    else:
        login_screen.destroy()
        main()

def main():
    global connection, entry_name, pizza_combo, drink_combo, extras_var, extras_options

    connection = create_database_connection()
    create_tables(connection)

    root = tk.Tk()
    root.title("House Pizza")
    root.configure(background='#edd76b')

    extras_options = ["Patates", "Sufle", "Tavuk Topları", "Tavuk Göğsü Parçaları", "Nugget", "Soğan Halkası"]

    create_widgets(root)

    root.mainloop()

    connection.close()

def create_widgets(root):
    global entry_name, pizza_combo, drink_combo, extras_var, extras_options

    label_name = tk.Label(root, text="Müşteri Adı:", bg="#edd76b")
    entry_name = tk.Entry(root)

    label_pizza = tk.Label(root, text="Pizza Seçimi:", bg="#edd76b")
    pizza_options = ["Margarita", "Pepperoni", "Vegetarian", "Hawaiian"]
    pizza_combo = ttk.Combobox(root, values=pizza_options)

    label_drink = tk.Label(root, text="İçecek Seçimi:", bg="#edd76b")
    drink_options = ["Coca-Cola", "Fuse Tea", "Fanta", "Sprite", "Ayran"]
    drink_combo = ttk.Combobox(root, values=drink_options)

    label_extras = tk.Label(root, text="Ekstralar", bg="#edd76b")
    extras_var = [tk.IntVar() for _ in range(len(extras_options))]
    extras_checkboxes = [tk.Checkbutton(root, text=extra, variable=extras_var[i], bg="#edd76b") for i, extra in enumerate(extras_options)]

    button_order = tk.Button(root, text="Sipariş Ver", command=place_order)
    button_view_data = tk.Button(root, text="Verileri Görüntüle", command=view_data)


    label_name.grid(row=0, column=0, sticky=tk.E, pady=5, padx=5)
    entry_name.grid(row=0, column=1, pady=5, padx=5)
    label_pizza.grid(row=1, column=0, sticky=tk.E, pady=5, padx=5)
    pizza_combo.grid(row=1, column=1, pady=5, padx=5)
    label_drink.grid(row=2, column=0, sticky=tk.E, pady=5, padx=5)
    drink_combo.grid(row=2, column=1, pady=5, padx=5)
    label_extras.grid(row=3, column=0, pady=5)
    for i, checkbox in enumerate(extras_checkboxes):
        checkbox.grid(row=4 + i // 2, column=i % 2, sticky=tk.W, pady=2, padx=5)
    button_order.grid(row=7, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W + tk.E)
    button_view_data.grid(row=8, column=0, columnspan=2, pady=5, padx=5, sticky=tk.W + tk.E)

if __name__ == "__main__":
    login_screen()
