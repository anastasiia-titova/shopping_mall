Модель информационной системы торгового центра, оснащенного несколькими кассовыми апаратами

Этот проект представляет собой систему управления товаром для торгового центра, где создаются окна для различных магазинов (Электроника, Одежда, Продукты)
и осуществляется покупка товаров.Программа использует базу данных PostgreSQL для хранения информации о товарах и покупках, а также многопоточность для
создания параллельных окон магазинов.

Основной скрипт программы создает три отдельных окна (по одному на каждый магазин) с использованием многопоточности. Каждое окно отображает список товаров,
доступных в соответствующем магазине. Пользователь может:
Выбрать товар из списка.
Ввести количество товара.
Нажать кнопку "Купить".
Программа проверяет наличие товара на складе, обновляет количество в таблице соответствующего магазина и записывает покупку в таблицу purchases.
Вся работа с окнами и покупками выполняется в отдельных потоках, что обеспечивает параллельное взаимодействие с несколькими магазинами одновременно.
