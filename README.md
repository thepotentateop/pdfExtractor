# PDF Extractor Application

This project is a FastAPI application that provides a set of endpoints for user authentication, file upload, and PDF extraction. It includes rate limiting, JWT authentication, and basic password hashing.

## Features

- **Authentication:** JWT-based token issuance.
- **Rate Limiting:** Basic IP-based rate limiting to control the number of requests.
- **File Handling:** Uploading and processing files.
- **PDF Extraction:** Extracting headers and items from uploaded PDFs.

## Prerequisites

- Python 3.8+
- Pip (Python package manager)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/your-repository.git
   cd your-repository
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows use: env\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   Create a `.env` file in the root directory and add the following environment variables:

   ```ini
   SECRET_KEY=your_secret_key
   ```

   Replace `your_secret_key` with a strong secret key for JWT encoding.

## Configuration

### OAuth2 Settings

- **SECRET_KEY:** The key used for encoding and decoding JWT tokens.
- **ALGORITHM:** The algorithm used for encoding the JWT tokens (default is `HS256`).
- **ACCESS_TOKEN_EXPIRE_MINUTES:** The duration for which the access token is valid.

### Rate Limiting

- **RATE_LIMIT:** Maximum number of requests allowed per time window (default: 100).
- **TIME_WINDOW:** Time window for rate limiting (default: 1 minute).

### File Uploads

- **UPLOAD_FOLDER:** Directory where uploaded files are saved (default: `uploads`).

## Running the Application

To start the FastAPI server, use:

```bash
uvicorn main:app --reload
```

Replace `main` with the name of your Python file if it’s different.

## API Endpoints

### `/token` (POST)

**Description:** Authenticates a user and returns a JWT access token.

**Request Form Parameters:**

- `username` (str): The username of the user.
- `password` (str): The password of the user.

**Response:**

- `access_token` (str): The JWT access token.
- `token_type` (str): The type of token (should be `bearer`).

**Errors:**

- `401 Unauthorized`: Incorrect username or password.

### `/users/me` (GET)

**Description:** Retrieves information about the current authenticated user.

**Authorization:** Requires a valid JWT token in the `Authorization` header.

**Response:**

- `username` (str): The username of the current user.

**Errors:**

- `401 Unauthorized`: Invalid or missing JWT token.

### `/upload` (POST)

**Description:** Uploads a file in base64 encoded format.

**Request Body:**

- `base64_string` (str): Base64 encoded string of the file.

**Response:**

- `file_id` (str): Unique identifier for the uploaded file.
- `file_path` (str): Path where the file is saved.

**Errors:**

- `500 Internal Server Error`: Error processing the file.

### `/extract-header` (POST)

**Description:** Extracts header information from an uploaded PDF.

**Request Body:**

- `file_id` (str): The unique identifier of the file.
- `keywords` (List[str]): List of keywords to search for in the PDF.
- `prompt` (str): Additional prompt for extraction.

**Response:**

- `header_info` (dict): Extracted header information.

**Errors:**

- `404 Not Found`: File not found.
- `500 Internal Server Error`: Error extracting data.

### `/extract-items` (POST)

**Description:** Extracts item information from an uploaded PDF.

**Request Body:**

- `file_id` (str): The unique identifier of the file.
- `keywords` (List[str]): List of keywords to search for in the PDF.
- `prompt` (str): Additional prompt for extraction.

**Response:**

- `item_info` (dict): Extracted item information.

**Errors:**

- `404 Not Found`: File not found.
- `500 Internal Server Error`: Error extracting data.

## Logging

The application uses Python's built-in logging module to log various events. Logs are output to the console.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## Contact

For questions or issues, please contact [akumar2@tsp.tech](mailto:yourname@example.com).
```

### Notes:
1. **Environment Variables:** Make sure to include any sensitive information, such as `SECRET_KEY`, in the environment variables for security reasons.
2. **Error Handling:** Ensure your application handles different types of errors gracefully and provides meaningful messages.
3. **Security Considerations:** This example assumes a basic level of security. For a production environment, consider implementing additional security measures such as HTTPS and more sophisticated error handling.

Feel free to modify this `README.md` to better suit your application's specifics or additional features.