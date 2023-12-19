import spacy
import csv
from nltk import ne_chunk, pos_tag
from nltk.chunk import conlltags2tree, tree2conlltags
from nltk.tokenize import word_tokenize
from nltk.tag import StanfordNERTagger
from nltk.parse import CoreNLPParser
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime
from nltk.corpus import stopwords
from nltk import download
from neo4j import GraphDatabase,basic_auth

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Stanford NER setup #install the ner files and paste the path here
stanford_ner_path = '/Users/grahulkrishna/Desktop/stanford-ner-2018-10-16/stanford-ner.jar'
stanford_classifier_path = '/Users/grahulkrishna/Desktop/stanford-ner-2018-10-16/classifiers/english.all.3class.distsim.crf.ser.gz'

# Stanford NER Tagger
stanford_ner_tagger = StanfordNERTagger(stanford_classifier_path, stanford_ner_path, encoding='utf-8')

# Stanford NLP Parser
stanford_parser = CoreNLPParser(url='http://localhost:9000')

#download('stopwords')
#nltk stopwords
nltk_stop_words = set(stopwords.words('english'))

# Additional stop words for symbols
additional_stop_words = set(nltk_stop_words|{'(', ')', ',', '.', ':', ';', '"', "'", '[', ']', '{', '}', 'and', 'but', 'or', 'if', 'because', 'while', 'for', 'so', 'nor', 'although', 'after', 'before', 'when', 'as', 'because', 'of', 'at', 'by', 'for', 'from', 'in', 'into', 'of', 'on', 'to', 'with', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't",'O'})

# Function to extract entities using spaCy
def extract_entities_spacy(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents if ent.text.lower() not in additional_stop_words]
    return entities

# Function to extract entities using NLTK
def extract_entities_nltk(text):
    tokens = word_tokenize(text)
    pos_tags = pos_tag(tokens)
    chunked = ne_chunk(pos_tags)
    iob_tags = tree2conlltags(chunked)
    entities = [(token, ner) for token, pos, ner in iob_tags if ner != 'O' and token.lower() not in additional_stop_words]
    return entities

# Function to extract entities using Stanford NER
def extract_entities_stanford_ner(text):
    entities = stanford_ner_tagger.tag(word_tokenize(text))
    entities = [(token, ner) for token, ner in entities if token.lower() not in additional_stop_words]
    return entities

# Function to extract combined entities from text using spaCy, NLTK, and Stanford NER
def extract_combined_entities(text):
    entities_spacy = extract_entities_spacy(text)
    entities_nltk = extract_entities_nltk(text)
    entities_stanford_ner = extract_entities_stanford_ner(text)

    combined_entities = set(entities_spacy + entities_nltk + entities_stanford_ner)
    return combined_entities

# Function to create nodes and relationships in Neo4j
def create_nodes_and_relationships(tx, node_type, node_label, edge_label, start_node, end_node):
    query = (
        f"MERGE (start:{start_node['type']} {{label: $start_label}}) "
        f"MERGE (end:{end_node['type']} {{label: $end_label}}) "
        f"CREATE (start)-[:{edge_label}]->(end)"
    )
    tx.run(query, start_label=start_node['label'], end_label=end_node['label'])

def KG_Pull_Requests(pull_requests_info):
    # Extract entities and relationships for each pull request
    knowledge_graph = nx.Graph()

    # Initialize a colormap for node types
    light_colormap = {
        'Pull_Request':'lightpink',
        'Author': 'lightblue',
        'State': 'lightgreen',
        'Timestamp': 'lightsalmon',
        'Commits': 'lightcoral',
        'Commit_ID': 'thistle',
        'Commit_Timestamp':'lightyellow',
    }

    for pr_number, pr_info in pull_requests_info.items():
        # Add nodes for pull request and author
        knowledge_graph.add_node(pr_number, type='Pull_Request', label=f'PR-{pr_number}')
        knowledge_graph.add_node(pr_info['Pull_Request_Author'], type='Author', label=pr_info['Pull_Request_Author'])
        knowledge_graph.add_edge(pr_number, pr_info['Pull_Request_Author'], relation='authored_by')

        # Add node for PR state
        knowledge_graph.add_node(pr_info['Pull_Request_State'], type='State', label=pr_info['Pull_Request_State'])
        knowledge_graph.add_edge(pr_number, pr_info['Pull_Request_State'], relation='has_state')

        # Add node for timestamp
        timestamp_node = pr_info['Time_Stamps']
        knowledge_graph.add_node(timestamp_node, type='Timestamp', label=timestamp_node)
        knowledge_graph.add_edge(pr_number, timestamp_node, relation='closed_at')

        # Add node for no. of commits
        no_of_commits = pr_info['Number_of_commits']
        knowledge_graph.add_node(no_of_commits, type='Commits', label=f'Commits: {no_of_commits}')
        knowledge_graph.add_edge(pr_number, no_of_commits, relation='has_commits')

        for commit_info in pr_info['Commits_Data']:
            commit_id = commit_info['Commit_ID']
            commit_message = commit_info['Commit_Message']

            # Add node for commit ID
            knowledge_graph.add_node(commit_id, type='Commit_ID', label=f'Commit: {commit_id[:7]}')
            knowledge_graph.add_edge(no_of_commits, commit_id, relation='includes_commit')

            # Extract entities from commit message
            commit_entities = extract_combined_entities(commit_message)

            for entity, entity_type in commit_entities:
                # Add nodes and edges for entities in commit message
                knowledge_graph.add_node(entity, type=entity_type, label=entity)
                knowledge_graph.add_edge(commit_id, entity, relation='mentions_entity')

                # Add nodes and edges for file changes
                file_change_type = entity_type + '_Change'
                knowledge_graph.add_node(file_change_type, type=file_change_type, label=entity_type)
                knowledge_graph.add_edge(commit_id, file_change_type, relation='includes_file_change')

                # Add nodes and edges for commit timestamp
                commit_timestamp = commit_info['Commit_Timestamp']
                if commit_timestamp is not None:
                    commit_timestamp_node = commit_timestamp
                    knowledge_graph.add_node(commit_timestamp_node, type='Commit_Timestamp', label=commit_timestamp)
                    knowledge_graph.add_edge(commit_id, commit_timestamp_node, relation='committed_at')


    # Set a default color for nodes not in the colormap
    default_color = 'gray'
    colormap = defaultdict(lambda: default_color, light_colormap)

    # Visualize the knowledge graph with lighter colors
    fig, ax = plt.subplots(figsize=(18, 12))
    pos = nx.spring_layout(knowledge_graph, seed=42)

    # Use light colors for nodes
    node_colors = [light_colormap.get(knowledge_graph.nodes[node]['type'], 'lightgray') for node in knowledge_graph.nodes]

    nx.draw_networkx_nodes(knowledge_graph, pos, node_size=800, node_color=node_colors, ax=ax)
    nx.draw_networkx_edges(knowledge_graph, pos, edge_color='gray', ax=ax)
    nx.draw_networkx_labels(knowledge_graph, pos, labels=nx.get_node_attributes(knowledge_graph, 'label'), font_size=8, font_color='black', font_weight='bold', ax=ax)

    # Add legends
    legend_labels = {node_type: plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10) for node_type, color in light_colormap.items()}
    plt.legend(legend_labels.values(), legend_labels.keys(), loc='upper right')

    plt.title("Knowledge Graph of Pull Requests, Authors, Timestamps, Commits, Entities, and File Changes")
    plt.savefig('op_prG.png')
    # Define the path to save the CSV file
    csv_file_path = 'knowledge_graph.csv'

    # Save nodes and edges to CSV file
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)

        # Write header row
        csv_writer.writerow(['Source', 'Target', 'Relation', 'Type', 'Label', 'Color'])

        # Write node and edge data
        for edge in knowledge_graph.edges(data=True):
            source, target, data = edge
            relation = data.get('relation', '')
            csv_writer.writerow([source, target, relation, '', '', ''])

        for node, data in knowledge_graph.nodes(data=True):
            node_type = data.get('type', '')
            label = data.get('label', '')
            color = data.get('color', '')
            csv_writer.writerow([node, '', '', node_type, label, color])

    print(f"Knowledge graph saved to: {csv_file_path}")
    # Save the plot as a TTL file
    ttl_filename = 'knowledge_graph.ttl'

    # Open the TTL file for writing
    with open(ttl_filename, 'w') as ttl_file:
        # Write the header
        ttl_file.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
        ttl_file.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")
        ttl_file.write("@prefix ex: <http://example.org/> .\n\n")

        # Iterate over nodes and write RDF triples
        for node, node_data in knowledge_graph.nodes(data=True):
            ttl_file.write(f"ex:{node} rdf:type ex:{node_data['type']} .\n")
            ttl_file.write(f"ex:{node} rdfs:label '{node_data['label']}' .\n")

        ttl_file.write("\n")

        # Iterate over edges and write RDF triples
        for edge in knowledge_graph.edges(data=True):
            subject, object, edge_data = edge
            ttl_file.write(f"ex:{subject} ex:{edge_data['relation']} ex:{object} .\n")

    print(f'The knowledge graph has been saved to {ttl_filename}.')
    # Connect to Neo4j Aura
    uri = "neo4j+s://9599df12.databases.neo4j.io"  # Replace with your Neo4j Aura database URI
    username = "neo4j"     # Replace with your Neo4j Aura username
    password = "0yQFGPzkZwlKkjCPTHs3-BXKnerNXVReCXIwV7nDJ4E"     # Replace with your Neo4j Aura password

    try:
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            with driver.session() as session:
                # Iterate over nodes and relationships in the NetworkX graph
                for node, node_data in knowledge_graph.nodes(data=True):
                    print(f"Processing node: {node}")
                    if node_data:
                        session.write_transaction(create_nodes_and_relationships, node_data['type'], node_data['label'], None, None, None)
                    else:
                        print(f"Skipping node {node} due to missing data")

                for edge in knowledge_graph.edges(data=True):
                    start_node, end_node, edge_data = edge
                    print(f"Processing edge: {start_node} - {edge_data['relation']} - {end_node}")
                    if edge_data:
                        session.write_transaction(create_nodes_and_relationships, None, None, edge_data['relation'], start_node, end_node)
                    else:
                        print(f"Skipping edge {start_node} - {edge_data['relation']} - {end_node} due to missing data")

    except Exception as e:
        print(f"Error connecting to Neo4j Aura: {e}")