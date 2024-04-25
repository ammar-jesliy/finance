# Finance - A Stock Trader Web App

Welcome to the Stock Trader Web App! This Flask application allows users to buy and sell stocks in a simulated stock market environment. Users can create accounts, manage their portfolios, and track their transactions seamlessly.

## Features

- __User Authentication:__ Users can create accounts and securely log in to manage their portfolios.
- __Stock Market Simulation:__ Utilizes real-time stock data to simulate a dynamic stock market environment.
- __Buy and Sell Stocks:__ Users can buy stocks at current market prices and sell stocks from their portfolio.
- __Portfolio Management:__ Users can view their current portfolio holdings and track their investment performance over time.
- __Transaction History:__ Detailed transaction history is provided to users for transparent tracking of their trades.

## Getting Started
To run the Stock Trader Web App locally on your machine, follow these steps:

1. Clone the repository to your local machine:
```
git clone https://github.com/ammar-jesliy/finance.git
```
2. Install the required dependencies:
```
pip install -r requirements.txt
```
3. Set up the database by running:
```
flask db upgrade
```
4. Start the Flask development server:
```
flask run
```
5. Open your web browser and navigate to http://localhost:5000 to access the application.

## Contributing
Contributions are welcome! If you find any bugs or have suggestions for improvements, please feel free to open an issue or submit a pull request.

## Acknowledgements
This project was completed as part of the CS50x course offered by Harvard University. Special thanks to the CS50 team for their guidance and support throughout the course.
