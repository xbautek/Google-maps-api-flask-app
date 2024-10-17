# Flask Web Service

This application is a Flask-based web service that provides weather data and nearby restaurant information using Google APIs. Application has also login and sign-up panel.

## Features
- Retrieve weather data
- Fetch nearby restaurant information based on user location
- Geolocation services

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/your-repo-name.git
    cd your-repo-name
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    venv\Scripts\activate  # On Windows
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    Create a `.env` file in the root directory and add your environment variables:
    ```properties
    GOOGLE_MAPS_API_KEY=your_google_maps_api_key
    OPENWEATHERMAP_API_KEY=your_openweathermap_api_key
    ```

5. Initialize the database:
    ```sh
    flask db init
    flask db migrate
    flask db upgrade
    ```

## Usage

1. Run the application:
    ```sh
    flask run
    ```

2. Access the application in your web browser at `http://127.0.0.1:5000`.

### Example API URLs

- **Get Weather Data**: `GET /weather`
- **Get Weather Data for a City**: `GET /api/weather/<city>`
- **Get Nearby Places**: `GET /api/places`
- **Geolocation**: `GET /api/geolocation`

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
