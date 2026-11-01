PRAGMA foreign_keys=ON;
CREATE TABLE customers(id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE);
CREATE TABLE profiles(id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL UNIQUE REFERENCES customers(id), bio TEXT NOT NULL);
CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id));
CREATE TABLE products(id INTEGER PRIMARY KEY, name TEXT NOT NULL, current_price_cents INTEGER NOT NULL CHECK(current_price_cents>=0));
CREATE TABLE order_items(
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK(quantity>0),
    unit_price_cents INTEGER NOT NULL CHECK(unit_price_cents>=0),
    PRIMARY KEY(order_id,product_id)
);
INSERT INTO customers VALUES(1,'anna@example.test');
INSERT INTO profiles VALUES(1,1,'Developer');
INSERT INTO orders VALUES(1,1);
INSERT INTO products VALUES(1,'Book',1500);
INSERT INTO order_items VALUES(1,1,2,1200);
