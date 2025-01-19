import psycopg2
import threading
import tkinter as tk
from tkinter import messagebox


# Функция для подключения к базе данных PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        dbname="shopping_mall",
        user="postgres",
        password="2460",
        host="localhost",
        port="5432"
    )
    return conn


# Функция для получения списка товаров из выбранного магазина
def get_products(store_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Определяем таблицу для каждого магазина
    if store_name == "Электроника":
        table_name = "electronics_products"
    elif store_name == "Одежда":
        table_name = "clothing_products"
    elif store_name == "Продукты":
        table_name = "grocery_products"
    else:
        return []

    query = f"SELECT product_id, name, price, quantity FROM {table_name}"
    cursor.execute(query)
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products


# Функция для совершения покупки товара
def make_purchase(store_name, product_id, quantity):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Определяем таблицу для каждого магазина
    if store_name == "Электроника":
        table_name = "electronics_products"
    elif store_name == "Одежда":
        table_name = "clothing_products"
    elif store_name == "Продукты":
        table_name = "grocery_products"
    else:
        messagebox.showerror("Ошибка", "Неизвестный магазин!")
        return

    try:
        # Проверяем, достаточно ли товара
        cursor.execute(f"SELECT quantity FROM {table_name} WHERE product_id = %s", (product_id,))
        available_quantity = cursor.fetchone()[0]

        if available_quantity >= quantity:
            # Уменьшаем количество товара в магазине
            cursor.execute(f"""
                UPDATE {table_name}
                SET quantity = quantity - %s
                WHERE product_id = %s
            """, (quantity, product_id))

            # Записываем покупку в таблицу покупок
            cursor.execute("""
                INSERT INTO purchases (store_name, product_name, price, quantity)
                SELECT %s, name, price, %s
                FROM """ + table_name + """ 
                WHERE product_id = %s
            """, (store_name, quantity, product_id))

            conn.commit()
            messagebox.showinfo("Успешно", "Покупка совершена!")
        else:
            messagebox.showwarning("Недостаточно товара", "Товара недостаточно на складе.")
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при совершении покупки: {e}")


# Функция для обработки покупки в отдельном потоке
def purchase_thread(store_name, product_id, quantity):
    threading.Thread(target=make_purchase, args=(store_name, product_id, quantity)).start()


# Функция для обновления списка товаров в интерфейсе
def update_product_list(store_name, product_listbox):
    products = get_products(store_name)
    product_listbox.delete(0, tk.END)  # Очищаем список
    for product in products:
        product_listbox.insert(tk.END, f"{product[1]} - {product[2]} руб. (Остаток: {product[3]})")


# Функция для создания интерфейса магазина
def create_store_app(store_name):
    window = tk.Tk()
    window.title(f"Магазин {store_name}")

    # Список товаров
    product_listbox = tk.Listbox(window, width=50, height=10)
    product_listbox.pack()

    # Обновление списка товаров
    update_product_list(store_name, product_listbox)

    # Количество товара
    quantity_label = tk.Label(window, text="Введите количество:")
    quantity_label.pack()

    quantity_entry = tk.Entry(window)
    quantity_entry.pack()

    # Кнопка "Купить"
    def on_buy_button():
        try:
            selected_product = product_listbox.get(tk.ACTIVE)
            if not selected_product:
                raise ValueError("Выберите товар для покупки.")
            product_name = selected_product.split(" - ")[0]
            quantity = int(quantity_entry.get())

            if quantity <= 0:
                raise ValueError("Количество должно быть положительным числом.")

            # Получаем product_id и цену из списка товаров
            conn = get_db_connection()
            cursor = conn.cursor()

            if store_name == "Электроника":
                table_name = "electronics_products"
            elif store_name == "Одежда":
                table_name = "clothing_products"
            elif store_name == "Продукты":
                table_name = "grocery_products"

            cursor.execute(f"SELECT product_id FROM {table_name} WHERE name = %s", (product_name,))
            product_id = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            # Запускаем покупку в отдельном потоке
            purchase_thread(store_name, product_id, quantity)

        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    buy_button = tk.Button(window, text="Купить", command=on_buy_button)
    buy_button.pack()

    window.mainloop()


# Функция для создания трех параллельных окон для магазинов
def create_multiple_store_apps():
    store_names = ["Электроника", "Одежда", "Продукты"]
    threads = []

    # Создаем отдельный поток для каждого магазина
    for store_name in store_names:
        thread = threading.Thread(target=create_store_app, args=(store_name,))
        threads.append(thread)
        thread.start()

    # Ожидаем завершения всех потоков
    for thread in threads:
        thread.join()


# Запуск приложения
if __name__ == "__main__":
    create_multiple_store_apps()
