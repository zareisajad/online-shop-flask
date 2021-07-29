# ProductPurchase
in this program you,
As a user you can:
- register and log in
- Add products to cart
- Filter products (most popular, most expensive, etc.)
- Order registration and payment

and as a admin:
- Ability to create a new product (image, description, price, discounted price, inventory, etc.)
- Ability to manage products
- Access the order list and details of each order

## Used:
- Python3
- Flask framework
- Bootstrap
- SQLite database 
## To Use:
- install python3, pip3, virtualenv
- clone the project 
- create a virtualenv named venv using ``` python -m venv venv ```
- Connect to virtualenv using ``` source venv/bin/activate ```
- from the project folder, install packages using ``` pip install -r requirements.txt ```
- for database migrations use : ``` flask db upgrade ```
- finally ``` flask run ```
