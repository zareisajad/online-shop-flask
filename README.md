# ProductPurchase
A simple product purchase app. user can add a product - [photo, title, price, discounted price, inventory ofand add some extra images for galley.]
the app shows a products page that user can see products and can add it to cart or see its details.
user also can manage [delete a product or see inventory and sold number] in another page that shows a list of all products.
in cart page user can add or reduce number of a product or remove it.
![Peek 2021-06-07 10-30](https://user-images.githubusercontent.com/71011395/120966627-b8c8bc00-c77b-11eb-875d-f463133cb32c.gif)
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
