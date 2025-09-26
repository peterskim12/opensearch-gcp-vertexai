import sys
from opensearchpy import OpenSearch
from google import genai
from google.genai.types import EmbedContentConfig

def query_opensearch(index, host='localhost', port=9200, user=None, password=None):

    client = OpenSearch(
        hosts=[{"host": host, "port": int(port)}],
        http_auth=(user, password) if user and password else None,
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False
    )

    genai_client = genai.Client()

    while True:
        query = input("Enter search query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
            
        # Generate vector representation of search query
        response = genai_client.models.embed_content(
            model="gemini-embedding-001",
            contents=[
                query
            ],
            config=EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",  # Optional
                output_dimensionality=3072
            ),
        )

        # body = {
        #     "query": {
        #         "multi_match": {
        #             "query": query,
        #             "fields": ["name", "description", "category", "brand"]
        #         }
        #     }
        # }

        body = {
            "query": {
                "knn": {
                    "description_vector": {
                        "vector": response.embeddings[0].values,
                        "k": 3
                    }
                }
            }
        }
        response = client.search(index=index, body=body, size=5)
        hits = response.get('hits', {}).get('hits', [])
        print(f"Found {len(hits)} results:")
        for hit in hits:
            print("Product Name: " + hit['_source']['name'] + ", Description: " + hit['_source']['description'] + ", Score: " + str(hit['_score']))
        print()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python query_opensearch.py <index_name> [host] [port] [user] [password]")
        sys.exit(1)
    index_name = sys.argv[1]
    host = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 9200
    user = sys.argv[4] if len(sys.argv) > 4 else None
    password = sys.argv[5] if len(sys.argv) > 5 else None
    query_opensearch(index_name, host, port, user, password)