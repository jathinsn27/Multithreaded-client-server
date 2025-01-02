# Distributed Server with Multi-Threading

## High-Level Design

This program implements a simple distributed server capable of handling HTTP requests and serving various file types (e.g., `.txt`, `.jpeg`, `.gif`, `.css`, `.js`). Below is a detailed description of its functionality:

1. **Server Initialization**:
   - The program starts with the `start_server` function, which binds to the localhost and port passed as parameters.
   - The server then listens for incoming connections.

2. **Request Dispatching**:
   - The `dispatcher` function accepts client connections and spawns a worker thread for each client request.
   - The worker thread handles the client request and executes the required operations.

3. **Request Handling**:
   - The `worker` function:
     - Manages the client connection using the `recv()` function.
     - Validates `GET` requests from the client.
     - Serves files of various types, such as `.txt`, `.jpeg`, `.gif`, `.css`, and `.js`.
     - Files served are sourced from the `https://lichess.org` website, downloaded using the `wget` command.

4. **HTTP Protocols**:
   - Supports both HTTP 1.0 and HTTP 1.1 protocols:
     - **HTTP 1.0**:
       - Non-persistent connections: Each request closes the connection and opens a new one.
     - **HTTP 1.1**:
       - Persistent connections with timeout handled by a dynamic heuristic timeout function.
       - The heuristic function calculates the timeout based on server load (number of active threads), with defined upper and lower bounds.

5. **Response Generation**:
   - The `send_response` function generates and sends response headers, including:
     - Protocol version
     - `Content-Type`
     - `Content-Length`
     - `Date`

6. **Edge Case Handling**:
   - Handles the following scenarios:
     - File not found (404)
     - No access permission (403)
     - Incorrect server run commands
     - Connection timeouts

---

## Folder Structure

```
.
|-- server.py         # Main server code
|-- files/            # Contains downloaded content of the lichess.org page
|-- readme.txt        # Documentation for running the program
```

---

## Instructions for Running the Program

### Prerequisites

1. Ensure that Python 3 or above is installed on your machine.
2. Use the `wget` command to download the files from `https://lichess.org` to your local machine:
   ```bash
   wget --recursive --level=1 --no-clobber --convert-links --no-parent --domains=lichess.org https://lichess.org/
   ```

### Running the Server

1. Navigate to the project directory.
2. Run the following command to start the server:
   ```bash
   python3 server.py -document_root "Distributed_server_socket/files" -port 9090
   ```

### Testing the Server

#### HTTP 1.0 Request

Use the following `curl` command on your terminal to test HTTP 1.0 requests:

```bash
curl --http1.0 http://localhost:9090/index.html
curl --http1.0 http://localhost:9090/index.php
```

#### HTTP 1.1 Request

1. Start the server.
2. Open a browser of your choice and connect to:
   ```
   http://localhost:9090
   ```

---

## Features

- Serves files of various types: `.txt`, `.jpeg`, `.gif`, `.css`, `.js`
- Supports both HTTP 1.0 and HTTP 1.1 protocols
- Dynamic timeout management for HTTP 1.1
- Handles common error scenarios (404, 403, timeouts)
- Multi-threaded request handling

---

## Notes

- Ensure the `files/` directory contains the downloaded content from `https://lichess.org`.
- The server is designed for educational purposes and may require additional security measures for deployment in production environments.

---

Enjoy using the distributed server!

