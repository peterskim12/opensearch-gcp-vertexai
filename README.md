# OpenSearch with Google Vertex AI Integration

This repository demonstrates how to use Google Vertex AI's Gemini embeddings with OpenSearch for semantic search capabilities.

## Project Structure

### Source Files (`src/`)

1. `index_jsonl_opensearch.py`: A script that indexes JSONL data into OpenSearch while generating vector embeddings using Google Vertex AI's Gemini model. The script:
   - Creates vector embeddings for product descriptions using the `gemini-embedding-001` model
   - Indexes documents into OpenSearch with both text fields and vector embeddings
   - Uses the index configuration specified in `data/index-config.json`

2. `query_opensearch.py`: An interactive script that performs semantic search queries using vector embeddings. The script:
   - Takes user input for search queries
   - Generates vector embeddings for the search queries using the same Gemini model
   - Performs k-NN (k-Nearest Neighbors) search in OpenSearch to find similar products
   - Returns the most semantically relevant results

### Data Files (`data/`)

1. `index-config.json`: OpenSearch index configuration file that defines:
   - Text field mappings for product attributes (name, description, category, etc.)
   - Vector field mapping for the description embeddings (3072-dimensional vectors)
   - Keyword field mappings for exact-match queries

2. `sample-products.jsonl`: Sample product data in JSONL format containing:
   - Product information including ID, name, category, brand, price, etc.
   - Detailed product descriptions used for generating embeddings
   - Various product attributes for demonstration purposes

## Setup Instructions

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   .\venv\Scripts\activate  # On Windows
   ```

2. Install required packages:
   ```bash
   pip install google-cloud-aiplatform  # For Vertex AI
   pip install opensearch-py           # For OpenSearch client
   ```

3. Ensure you have:
   - Access to a running OpenSearch cluster
   - Proper authentication credentials for Google Cloud/Vertex AI
   - The necessary permissions to use the Gemini API

## Usage

1. Index data:
   ```bash
   python src/index_jsonl_opensearch.py [jsonl_file] [index_name] [host] [port] [username] [password]
   ```

2. Search products:
   ```bash
   python src/query_opensearch.py [index_name] [host] [port] [username] [password]
   ```

The search interface will prompt you to enter search queries and will return the most semantically relevant products based on the vector similarity of your query to the product descriptions.

## License

See the [LICENSE](LICENSE) file for license rights and limitations.