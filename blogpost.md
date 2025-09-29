# Overview

Aiven for OpenSearch is the best way to run OpenSearch on Google Cloud. Aiven for OpenSearch is a fully-managed OpenSearch service that allows companies to run search applications without the burden and complexity of self-managing OpenSearch in the cloud.

Aiven for OpenSearch on GCP runs on Google Cloud's industry-leading cloud infrastructure--Google Compute Engine, Google Cloud Storage, Private Service Connect, and more--to provide exceptional performance-cost ratio while supporting enterprise grade security requirements. Aiven also offers native, out-of-the-box integrations with Google services such as Big Query, Pub/Sub, Cloud Logging, and others to provide a Google-native experience to your OpenSearch-based solution. Finally, Aiven lets you pay for your OpenSearch managed service through your Google account by making it available through the Google Cloud Marketplace. 

Companies like Adeo, Mirakl, and Priceline rely on Aiven for OpenSearch to support their mission-critical search and analytics workloads on Google Cloud. In this post, we'll show you how you can use Aiven for OpenSearch with Vertex AI to build a vector search application. 

Aiven for OpenSearch offers native vector search capabilities to support semantic search applications. Semantic search is different from traditional keyword search in that it considers user intent and meaning to improve the quality of search results. 

Semantic search requires converting text, both in the documents being search and the search query, into vector embeddings, which are numeric representations of words and phrases. Text can be converted into vector embeddings using a variety of models--the embedding model you choose will depend on factors such as performance, output size, cost, and domain-specific bias.

This is where Google Vertex AI comes into play--Vertex AI is a fully-managed, unified AI development platform that simplifies and accelerates the entire ML lifecycle to enable teams to collaborate using a common toolset. One of Vertex AI's capabilities is generating vector embeddings using the latest text embedding model from Google, Gemini Embedding 001, an open model such as E5, or any other supported model deployed in Vertex AI.

# Tutorial

## Pre-requisites

* Clone [this Github repo](https://github.com/peterskim12/opensearch-gcp-vertexai) for all the example code and data
* Follow the [instructions in this doc](https://cloud.google.com/vertex-ai/generative-ai/docs/start/api-keys?usertype=expressmode) with an active Google Cloud account to set up a development environment to use Vertex AI API
* Create an OpenSearch service on Aiven with [these instructions](https://aiven.io/docs/products/opensearch/get-started). 

## Indexing

The dataset we'll use in this tutorial is a small set of 20 sample records representing some products in a sports-related online retail store. These records can be found in the `data/sample-products.jsonl` file in the associated GitHub repo.

Here's what one of those records looks like:

```json
{
	"id": 10,
	"name": "Boxing Gloves",
	"category": "Boxing",
	"brand": "PunchForce",
	"price": 34.99,
	"stock": 100,
	"color": "Blue",
	"size": "12oz",
	"rating": 4.5,
	"description": "Train with confidence using these high-impact boxing gloves. The multi-layer padding absorbs shocks, and the secure wrist strap provides stability during intense workouts.",
	"sku": "BOX-010"
}
```

Instead of indexing these records into OpenSearch as-is, we'll use Vertex AI to generate a vector representation of the `description` field values before sending the record to OpenSearch. 

```python
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
```

For more details, see the [Gen AI SDK docs](https://googleapis.github.io/python-genai/genai.html#genai.models.Models.embed_content). 

In OpenSearch, we need to create an index mapping that expects a field containing a vector embedding, in this case `description_vector`. The index mapping and settings can be found in `data/index-config.json`.

In the index setting, we need to set "knn" to true:

```json
"settings": {
	"index": {
		"number_of_shards": "1",
		"number_of_replicas": "0",
		"knn": true
	}
}
```

And in the mapping definition for the `description_vector` field, we use type `knn_vector` and specify the number of dimensions:

```json
"description_vector": {
	"type": "knn_vector",
	"dimension": 3072
},
```

More details on the `knn_vector` type mapping can be found in the [OpenSearch documentation](https://docs.opensearch.org/latest/field-types/supported-field-types/knn-vector/). 

## Querying

When using OpenSearch for semantic search, you also have to convert the search query text into a vector representation. 

```python
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
```

Note that when you generate embeddings for the query, you need to specify the `RETRIEVAL_QUERY` task type instead of the `RETRIEVAL_DOCUMENT` task type we used when indexing the document earlier. For more details, see the [Vertex AI documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/task-types#retrieve_information_from_texts) on task types.

Now that we've indexed a few sample records and wrote the code for generating embeddings for the input search query, we can run some search queries. Our expectation should be that even if there is no textual match between the query and documents, using vector representations to perform a knn (nearest neighbor) search should return relevant documents.

The `query_opensearch.py` script provides an interactive prompt to ask for the search query and executes a knn search. 

When we search for "tottenham", the top hits are the "Football Jersey" and "Soccer Ball" products. Even though the term tottenham is not contained in either of those product records, the embedding model provides real world context that understands "tottenham" typically refers to a soccer/football club in North London. 

```
Enter search query (or 'exit' to quit): tottenham
Found 5 results:
Product Name: Football Jersey, Description: Show your team spirit with this breathable football jersey. The moisture-wicking fabric keeps you cool during games, and the reinforced stitching ensures long-lasting wear., Score: 0.574192
Product Name: Soccer Ball, Description: Engineered for optimal flight and control, this soccer ball is perfect for matches and practice. The reinforced bladder maintains shape and air retention, ensuring consistent performance on the field., Score: 0.5666915
```

When we search for "lululemon", the top hits are "Yoga Mat" and "Fitness Tracker". Similar to the example above, even though the term "lululemon" doesn't exist in the index, the vector embeddings clearly has the additional context to understand "lululemon" is highly relevant with yoga and fitness.

```
Enter search query (or 'exit' to quit): lululemon
Found 5 results:
Product Name: Yoga Mat, Description: This non-slip yoga mat offers superior grip and comfort for all your poses. Its extra thickness provides joint protection, and the lightweight design makes it easy to carry to classes or use at home., Score: 0.6023507
Product Name: Fitness Tracker, Description: Monitor your workouts and health stats with this advanced fitness tracker. The intuitive interface and long battery life make it a perfect companion for athletes and fitness enthusiasts., Score: 0.5859851
```

# Conclusion

We've demonstrated how with the power of Aiven for OpenSearch and Google Vertex AI, we're able to easily build a search application that delivers much more meaningful results than what has traditionally been possible with just keyword search. 

TODO: Call To Action