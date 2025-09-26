import json
import sys
from google import genai
from google.genai.types import EmbedContentConfig
from opensearchpy import OpenSearch

def index_jsonl_to_opensearch(jsonl_path, index_name, host='localhost', port=9200, user=None, password=None):
    
    # Create vertexai client
    genai_client = genai.Client()
    
    # Connect to OpenSearch
    auth = (user, password) if user and password else None
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False
    )

    # Load index mapping from data/index-config.json if it exists
    index_config = None
    with open('data/index-config.json', 'r') as index_conf_file:
        index_config = json.load(index_conf_file)

    # Create index if it doesn't exist
    if not client.indices.exists(index=index_name):
        client.indices.create(index=index_name, body=index_config)

    # Read and index each line
    with open(jsonl_path, 'r') as f:
        for line in f:
            doc = json.loads(line)

            # Generate vector embedding for description
            response = genai_client.models.embed_content(
                model="gemini-embedding-001",
                contents=[
                    doc["description"]
                ],
                config=EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",  # Optional
                    output_dimensionality=3072  # Optional
                ),
            )

            # Retrieve the generated embedding and 
            # store it in a field named description_vector
            if response.embeddings:
                doc["description_vector"] = response.embeddings[0].values

            client.index(index=index_name, body=doc)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python index_jsonl_opensearch.py <jsonl_file> <index_name> [host] [port] [user] [password]")
        sys.exit(1)
    jsonl_file = sys.argv[1]
    index_name = sys.argv[2]
    host = sys.argv[3] if len(sys.argv) > 3 else 'localhost'
    port = int(sys.argv[4]) if len(sys.argv) > 4 else 9200
    user = sys.argv[5] if len(sys.argv) > 5 else None
    password = sys.argv[6] if len(sys.argv) > 6 else None
    index_jsonl_to_opensearch(jsonl_file, index_name, host, port, user, password)
