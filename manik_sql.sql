-------------------------------
-- Базовые настройки
-------------------------------
DROP DATABASE IF EXISTS mvp_manik_db;
CREATE DATABASE mvp_manik_db
    WITH
    ENCODING = 'UTF8';
\c mvp_manik_db
SET client_encoding TO 'UTF8';
-------------------------------
-- Таблицы ядра системы
-------------------------------


-- Права доступа
CREATE TABLE Регулирование_Отношений (
    таблица TEXT PRIMARY KEY,
    видимость TEXT NOT NULL CHECK (видимость IN ('все', 'админ')) DEFAULT 'все',
    создание TEXT NOT NULL CHECK (создание IN ('все', 'админ')) DEFAULT 'все',
    обновление TEXT NOT NULL CHECK (обновление IN ('все', 'админ')) DEFAULT 'все',
    удаление TEXT NOT NULL CHECK (удаление IN ('все', 'админ')) DEFAULT 'все'
);

CREATE OR REPLACE FUNCTION добавить_отношение()
RETURNS EVENT_TRIGGER AS $$
DECLARE
    полное_имя_таблицы TEXT;
    имя_таблицы TEXT;
BEGIN
    -- Получаем полное имя таблицы (включая схему)
    SELECT object_identity INTO полное_имя_таблицы
    FROM pg_event_trigger_ddl_commands()
    WHERE command_tag = 'CREATE TABLE';

    -- Извлекаем только имя таблицы (без схемы)
    -- имя_таблицы := split_part(полное_имя_таблицы, '.', 2);
    имя_таблицы := regexp_replace(split_part(полное_имя_таблицы, '.', 2), '"', '', 'g');

    -- Вставляем запись в таблицу Регулирование_Отношений
    INSERT INTO Регулирование_Отношений (таблица, видимость)
    VALUES (имя_таблицы, 'все')
    ON CONFLICT DO NOTHING;
END;
$$ LANGUAGE plpgsql;

-- Создаем событийный триггер
CREATE EVENT TRIGGER триггер_добавить_отношение
ON ddl_command_end
WHEN TAG IN ('CREATE TABLE')
EXECUTE FUNCTION добавить_отношение();

INSERT INTO Регулирование_Отношений (таблица, видимость) VALUES ('Регулирование_Отношений','админ');


-- Квалификации
CREATE TABLE Квалификации (
    номер_квалификации SERIAL PRIMARY KEY,
    название TEXT NOT NULL UNIQUE,
    описание TEXT,
    удален BOOLEAN DEFAULT FALSE,
    дата_удаления TIMESTAMP
);

INSERT INTO Квалификации (название, описание) VALUES ('отсутствует','нет квалификации');

-- Сотрудники (с улучшенной безопасностью)
CREATE TABLE Сотрудники (
    номер_сотрудника SERIAL PRIMARY KEY,
    логин TEXT NOT NULL UNIQUE,
    пароль TEXT NOT NULL,
    фио TEXT NOT NULL,
    телефон TEXT,
    роль TEXT NOT NULL CHECK (роль IN ('мастер', 'оператор', 'админ')) DEFAULT 'оператор',
    квалификация INT REFERENCES Квалификации(номер_квалификации) DEFAULT 1,
    статус TEXT NOT NULL CHECK (статус IN ('активен', 'неактивен', 'в обработке')) DEFAULT 'в обработке',
    удален BOOLEAN DEFAULT FALSE,
    дата_удаления TIMESTAMP
);

-- Автоматическое назначение первого сотрудника администратором
CREATE OR REPLACE FUNCTION назначить_админа()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Сотрудники WHERE удален = FALSE) THEN
        NEW.роль := 'админ';
        NEW.статус := 'активен';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER триггер_назначения_админа
BEFORE INSERT ON Сотрудники
FOR EACH ROW EXECUTE FUNCTION назначить_админа();

INSERT INTO Сотрудники (логин, пароль, фио, квалификация) VALUES ('admin','admin','Administrator', 1);


CREATE OR REPLACE FUNCTION удаление_сотрудника()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.удален = TRUE AND OLD.статус IN ('в обработке', 'активен') THEN
        OLD.статус := 'неактивен';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER триггер_удаления_сотрудника
AFTER UPDATE ON Сотрудники
FOR EACH ROW EXECUTE FUNCTION удаление_сотрудника();



CREATE TABLE Графики_работы (
    номер_графика SERIAL PRIMARY KEY,
    сотрудник INT REFERENCES Сотрудники(номер_сотрудника),
    дата_начала TIMESTAMP,
    дата_конца TIMESTAMP,
    явка BOOLEAN DEFAULT FALSE,
    временные_промежутки JSONB DEFAULT '{}',
    удален BOOLEAN DEFAULT FALSE,
    дата_удаления TIMESTAMP,
    CHECK (дата_конца > дата_начала)
);

-------------------------------
-- Бизнес-логика
-------------------------------

-- Услуги
CREATE TABLE Услуги (
    номер_услуги SERIAL PRIMARY KEY,
    название TEXT NOT NULL,
    необходимая_квалификация INT REFERENCES Квалификации(номер_квалификации),
    описание TEXT,
    цена NUMERIC(10,2) CHECK (цена > 0),
    длительность INTERVAL,
    удален BOOLEAN DEFAULT FALSE,
    дата_удаления TIMESTAMP
);

-- Клиенты
CREATE TABLE Клиенты (
    номер_клиента SERIAL PRIMARY KEY,
    фио TEXT NOT NULL,
    телефон TEXT,
    удален BOOLEAN DEFAULT FALSE,
    дата_удаления TIMESTAMP
);

-- Заказы с улучшенной автоматизацией
CREATE TABLE Заказы (
    номер_заказа SERIAL PRIMARY KEY,
    клиент INT NOT NULL REFERENCES Клиенты(номер_клиента),
    услуга INT NOT NULL REFERENCES Услуги(номер_услуги),
    мастер INT REFERENCES Сотрудники(номер_сотрудника),
    дата_начала TIMESTAMP,
    длительность INTERVAL,
    статус TEXT NOT NULL CHECK (статус IN ('принят', 'в работе', 'завершен', 'отменен')) DEFAULT 'принят',
    способ_оплаты TEXT CHECK (способ_оплаты IN ('наличные', 'карта')),
    цена NUMERIC(10,2),
    удален BOOLEAN DEFAULT FALSE,
    дата_удаления TIMESTAMP
);

-- Автоматическое копирование цены из услуги
CREATE OR REPLACE FUNCTION обновить_цену_заказа()
RETURNS TRIGGER AS $$
BEGIN
    SELECT цена, длительность INTO NEW.цена, NEW.длительность
    FROM Услуги
    WHERE номер_услуги = NEW.услуга;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER триггер_цены_заказа
BEFORE INSERT ON Заказы
FOR EACH ROW EXECUTE FUNCTION обновить_цену_заказа();

-------------------------------
-- Архивация данных
-------------------------------

-- Архив заказов
CREATE TABLE Архив_заказов (
    номер_заказа INT PRIMARY KEY REFERENCES Заказы(номер_заказа),
    данные JSONB NOT NULL,
    дата_архивации TIMESTAMP DEFAULT NOW()
);

-- Автоматическая архивация при завершении
CREATE OR REPLACE FUNCTION архив_заказов()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.статус IN ('завершен', 'отменен') THEN
        INSERT INTO Архив_заказов (номер_заказа, данные)
        VALUES (NEW.номер_заказа, row_to_json(NEW));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER триггер_архивации
AFTER UPDATE ON Заказы
FOR EACH ROW EXECUTE FUNCTION архив_заказов();

-------------------
-- Ресурсы
-------------------
-- Инвентарь
CREATE TABLE Инвентарь (
    номер_предмета SERIAL PRIMARY KEY,
    название TEXT NOT NULL,
    тип TEXT NOT NULL CHECK (тип IN ('расходник', 'инструмент')),
    количество INT NOT NULL CHECK (количество >= 0),
    последняя_поставка DATE,
    цена_за_единицу NUMERIC(10,2) CHECK (цена_за_единицу >= 0),
    удален BOOLEAN DEFAULT false,
    дата_удаления TIMESTAMP
);

-------------------------------
-- Управление доступом
-------------------------------

CREATE TABLE Регулирование_Квалификации(
    название TEXT PRIMARY KEY,
    видимость_в_отношении TEXT CHECK (видимость_в_отношении IN ('админ', 'все')) DEFAULT 'все',
    видимость_в_попапе TEXT CHECK (видимость_в_попапе IN ('все', 'создание', 'обновление', 'нет')) DEFAULT 'все'
);


CREATE OR REPLACE FUNCTION log_table_columns_квалификации()
RETURNS VOID AS $$
DECLARE
    column_record RECORD;
BEGIN
    FOR column_record IN
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'Квалификации'
    LOOP
        INSERT INTO Регулирование_Квалификации (название)
        VALUES (column_record.column_name)
        ON CONFLICT (название) DO NOTHING;
    END LOOP;
    RAISE NOTICE 'Функция завершена';
END;
$$ LANGUAGE plpgsql;

-- Вызов функции после создания таблиц
SELECT log_table_columns_квалификации();


CREATE TABLE Регулирование_Сотрудники(
    название TEXT PRIMARY KEY,
    видимость_в_отношении TEXT CHECK (видимость_в_отношении IN ('админ', 'все')) DEFAULT 'все',
    видимость_в_попапе TEXT CHECK (видимость_в_попапе IN ('все', 'создание', 'обновление', 'нет')) DEFAULT 'все'

);


CREATE OR REPLACE FUNCTION log_table_columns_сотрудники()
RETURNS VOID AS $$
DECLARE
    column_record RECORD;
BEGIN
    FOR column_record IN
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'Сотрудники' 
    LOOP
        INSERT INTO Регулирование_Сотрудники (название)
        VALUES (column_record.column_name)
        ON CONFLICT (название) DO NOTHING;
    END LOOP;
    RAISE NOTICE 'Функция завершена';
END;
$$ LANGUAGE plpgsql;

-- Вызов функции после создания таблиц
SELECT log_table_columns_сотрудники();

CREATE TABLE Регулирование_Графики_работы(
    название TEXT PRIMARY KEY,
    видимость_в_отношении TEXT CHECK (видимость_в_отношении IN ('админ', 'все')) DEFAULT 'все',
    видимость_в_попапе TEXT CHECK (видимость_в_попапе IN ('все', 'создание', 'обновление', 'нет')) DEFAULT 'все'
);


CREATE OR REPLACE FUNCTION log_table_columns_графики_работы()
RETURNS VOID AS $$
DECLARE
    column_record RECORD;
BEGIN
    FOR column_record IN
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'Графики_работы'
    LOOP
        INSERT INTO Регулирование_Графики_работы (название)
        VALUES (column_record.column_name)
        ON CONFLICT (название) DO NOTHING;
    END LOOP;
    RAISE NOTICE 'Функция завершена';
END;
$$ LANGUAGE plpgsql;

-- Вызов функции после создания таблиц
SELECT log_table_columns_графики_работы();

CREATE TABLE Регулирование_Услуги(
    название TEXT PRIMARY KEY,
    видимость_в_отношении TEXT CHECK (видимость_в_отношении IN ('админ', 'все')) DEFAULT 'все',
    видимость_в_попапе TEXT CHECK (видимость_в_попапе IN ('все', 'создание', 'обновление', 'нет')) DEFAULT 'все'

);


CREATE OR REPLACE FUNCTION log_table_columns_услуги()
RETURNS VOID AS $$
DECLARE
    column_record RECORD;
BEGIN
    FOR column_record IN
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'Услуги'
    LOOP
        INSERT INTO Регулирование_Услуги (название)
        VALUES (column_record.column_name)
        ON CONFLICT (название) DO NOTHING;
    END LOOP;
    RAISE NOTICE 'Функция завершена';
END;
$$ LANGUAGE plpgsql;

-- Вызов функции после создания таблиц
SELECT log_table_columns_услуги();

CREATE TABLE Регулирование_Клиенты(
    название TEXT PRIMARY KEY,
    видимость_в_отношении TEXT CHECK (видимость_в_отношении IN ('админ', 'все')) DEFAULT 'все',
    видимость_в_попапе TEXT CHECK (видимость_в_попапе IN ('все', 'создание', 'обновление', 'нет')) DEFAULT 'все'
   
);


CREATE OR REPLACE FUNCTION log_table_columns_клиенты()
RETURNS VOID AS $$
DECLARE
    column_record RECORD;
BEGIN
    FOR column_record IN
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'Клиенты'
    LOOP
        INSERT INTO Регулирование_Клиенты (название)
        VALUES (column_record.column_name)
        ON CONFLICT (название) DO NOTHING;
    END LOOP;
    RAISE NOTICE 'Функция завершена';
END;
$$ LANGUAGE plpgsql;

-- Вызов функции после создания таблиц
SELECT log_table_columns_клиенты();


CREATE TABLE Регулирование_Заказы(
    название TEXT PRIMARY KEY,
    видимость_в_отношении TEXT CHECK (видимость_в_отношении IN ('админ', 'все')) DEFAULT 'все',
    видимость_в_попапе TEXT CHECK (видимость_в_попапе IN ('все', 'создание', 'обновление', 'нет')) DEFAULT 'все'

);


CREATE OR REPLACE FUNCTION log_table_columns_заказы()
RETURNS VOID AS $$
DECLARE
    column_record RECORD;
BEGIN
    FOR column_record IN
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'Заказы'
    LOOP
        INSERT INTO Регулирование_Заказы (название)
        VALUES (column_record.column_name)
        ON CONFLICT (название) DO NOTHING;
    END LOOP;
    RAISE NOTICE 'Функция завершена';
END;
$$ LANGUAGE plpgsql;

-- Вызов функции после создания таблиц
SELECT log_table_columns_заказы();

CREATE TABLE Регулирование_Архив_заказов(
    название TEXT PRIMARY KEY,
    видимость_в_отношении TEXT CHECK (видимость_в_отношении IN ('админ', 'все')) DEFAULT 'все',
    видимость_в_попапе TEXT CHECK (видимость_в_попапе IN ('все', 'создание', 'обновление', 'нет')) DEFAULT 'все'

);


CREATE OR REPLACE FUNCTION log_table_columns_архив_заказов()
RETURNS VOID AS $$
DECLARE
    column_record RECORD;
BEGIN
    FOR column_record IN
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'Архив_заказов'
    LOOP
        INSERT INTO Регулирование_Архив_заказов (название)
        VALUES (column_record.column_name)
        ON CONFLICT (название) DO NOTHING;
    END LOOP;
    RAISE NOTICE 'Функция завершена';
END;
$$ LANGUAGE plpgsql;

-- Вызов функции после создания таблиц
SELECT log_table_columns_архив_заказов();


CREATE TABLE Регулирование_Инвентарь(
    название TEXT PRIMARY KEY,
    видимость_в_отношении TEXT CHECK (видимость_в_отношении IN ('админ', 'все')) DEFAULT 'все',
    видимость_в_попапе TEXT CHECK (видимость_в_попапе IN ('все', 'создание', 'обновление', 'нет')) DEFAULT 'все'

);


CREATE OR REPLACE FUNCTION log_table_columns_инвентарь()
RETURNS VOID AS $$
DECLARE
    column_record RECORD;
BEGIN
    FOR column_record IN
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'Инвентарь'
    LOOP
        INSERT INTO Регулирование_Инвентарь (название)
        VALUES (column_record.column_name)
        ON CONFLICT (название) DO NOTHING;
    END LOOP;
    RAISE NOTICE 'Функция завершена';
END;
$$ LANGUAGE plpgsql;

-- Вызов функции после создания таблиц
SELECT log_table_columns_инвентарь();
