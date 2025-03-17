# README.md

# Mini E-Commerce Flask Application

This project is a mini e-commerce application built using Flask. It allows users to browse products, place orders, and
interact with a Telegram bot for order processing and updates.

## Project Structure

```
mini_ecom_flask
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── payments.py
│   ├── bot.py
│   └── bot_handlers.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd mini_ecom_flask
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```
   python app/main.py
   ```

5. **Start the Telegram bot:**
   ```
   python app/bot.py
   ```

## Usage

- Use the `/shop` command in the Telegram bot to browse products.
- Add items to your cart and proceed to checkout.
- Enter your shipping address and confirm payment through the provided QR code.

## Dependencies

- Flask
- SQLAlchemy
- python-telegram-bot

## License

This project is licensed under the MIT License.

uninstall all
pip freeze | grep -v "^-e" | xargs pip uninstall -y