# Getting Started

This guide will help you get started with the API Credential service.

## Prerequisites

Before you begin, make sure you have the following:

- Python 3.8 or higher
- Docker (optional, for containerized deployment)
- Access to the Karned platform

## Installation

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/Karned/Kommon/api-credential.git
   cd api-credential
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`.

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t api-credential .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 api-credential
   ```

## Configuration

The API Credential service can be configured using environment variables or a configuration file. See the [configuration documentation](development/setup.md#configuration) for more details.

## Authentication

To authenticate with the API, you need to obtain an API token. See the [authentication documentation](api/overview.md#authentication) for more details.

## Next Steps

- Explore the [API Reference](api/overview.md) to learn about the available endpoints
- Learn about [development and contributing](development/contributing.md) to the project