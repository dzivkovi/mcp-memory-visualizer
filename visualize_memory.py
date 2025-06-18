#!/usr/bin/env python3
"""
Static Memory Visualization for Claude MCP

Creates static network analysis and visualization of memory.json files from
Anthropic's Memory MCP server using NetworkX and Matplotlib. Features include:
- Statistical analysis of entities and relationships
- Network centrality and connectivity metrics
- Redundancy detection for memory cleanup
- High-resolution graph visualization
- Color-coded entity types with legends

Requires: pip install networkx matplotlib
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict, Counter

def load_memory_file(file_path):
    """Load and parse memory.json file"""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    entities = []
    relations = []
    
    for line in lines:
        if line.strip():
            data = json.loads(line.strip())
            if data.get('type') == 'entity':
                entities.append(data)
            elif data.get('type') == 'relation':
                relations.append(data)
    
    return entities, relations

def create_graph(entities, relations):
    """Create NetworkX graph from entities and relations"""
    G = nx.Graph()
    
    # Add nodes (entities)
    for entity in entities:
        G.add_node(
            entity['name'],
            entity_type=entity['entityType'],
            observations=len(entity['observations'])
        )
    
    # Add edges (relations)
    for relation in relations:
        if relation['from'] in G.nodes and relation['to'] in G.nodes:
            G.add_edge(
                relation['from'],
                relation['to'],
                relation_type=relation['relationType']
            )
    
    return G

def analyze_graph(G):
    """Comprehensive graph analysis with network metrics"""
    print("✨ === MEMORY GRAPH ANALYSIS ===")
    print(f"📊 Total entities: {G.number_of_nodes()}")
    print(f"🔗 Total relationships: {G.number_of_edges()}")
    print(f"📋 Connected components: {nx.number_connected_components(G)}")
    
    # Entity types distribution
    entity_types = [G.nodes[node]['entity_type'] for node in G.nodes()]
    type_counts = Counter(entity_types)
    print("\nEntity Types:")
    for entity_type, count in type_counts.most_common():
        print(f"  {entity_type}: {count}")
    
    # Find isolated nodes (no connections)
    isolated = list(nx.isolates(G))
    if isolated:
        print(f"\n🏠 Isolated entities (consider removing): {len(isolated)}")
        for node in isolated[:5]:  # Show first 5
            print(f"  • {node} ({G.nodes[node]['entity_type']})")
        if len(isolated) > 5:
            print(f"  ... and {len(isolated) - 5} more")
    
    # Most connected entities
    degree_centrality = nx.degree_centrality(G)
    top_connected = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"\n🌐 Most connected entities:")
    for node, centrality in top_connected:
        print(f"  • {node}: {G.degree[node]} connections")
    
    print("=" * 40)

def visualize_graph(G, output_file="memory_graph.png"):
    """Create high-quality static visualization"""
    plt.figure(figsize=(16, 12))
    plt.style.use('default')  # Clean matplotlib style
    
    # Color nodes by entity type
    entity_types = [G.nodes[node]['entity_type'] for node in G.nodes()]
    unique_types = list(set(entity_types))
    colors = plt.cm.Set3(range(len(unique_types)))
    color_map = dict(zip(unique_types, colors))
    node_colors = [color_map[G.nodes[node]['entity_type']] for node in G.nodes()]
    
    # Node sizes based on number of observations
    node_sizes = [G.nodes[node]['observations'] * 100 + 200 for node in G.nodes()]
    
    # Use spring layout for natural node positioning
    try:
        pos = nx.spring_layout(G, k=3, iterations=50, seed=42)  # Reproducible layout
    except:
        pos = nx.circular_layout(G)
    
    # Draw the graph
    nx.draw(G, pos, 
            node_color=node_colors,
            node_size=node_sizes,
            with_labels=True,
            font_size=8,
            font_weight='bold',
            edge_color='gray',
            alpha=0.7)
    
    # Create legend
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                 markerfacecolor=color_map[entity_type], 
                                 markersize=10, label=entity_type)
                      for entity_type in unique_types]
    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
    
    plt.title("Claude MCP Memory Graph\n(Node size = # observations, Colors = Entity types)", 
              fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ High-resolution graph saved as {output_file}")
    plt.show()

def find_redundancies(entities, relations):
    """Find potential redundancies for memory optimization"""
    print("\n🔍 === REDUNDANCY ANALYSIS ===")
    
    # Find similar entity names
    names = [entity['name'] for entity in entities]
    similar_pairs = []
    for i, name1 in enumerate(names):
        for j, name2 in enumerate(names[i+1:], i+1):
            if name1.lower() in name2.lower() or name2.lower() in name1.lower():
                if name1 != name2:
                    similar_pairs.append((name1, name2))
    
    if similar_pairs:
        print("🔀 Potentially similar entities (consider merging):")
        for pair in similar_pairs[:5]:  # Show first 5
            print(f"  • '{pair[0]}' vs '{pair[1]}'")
        if len(similar_pairs) > 5:
            print(f"  ... and {len(similar_pairs) - 5} more pairs")
    
    # Find entities with very few observations
    sparse_entities = [e for e in entities if len(e['observations']) <= 1]
    if sparse_entities:
        print(f"\n📎 Entities with minimal info (consider removing): {len(sparse_entities)}")
        for entity in sparse_entities[:5]:  # Show first 5
            print(f"  • {entity['name']}: {len(entity['observations'])} observation(s)")
        if len(sparse_entities) > 5:
            print(f"  ... and {len(sparse_entities) - 5} more entities")

def main():
    # Load memory file (demo file included, or use your own memory.json)
    memory_file = "memory.json"
    
    try:
        entities, relations = load_memory_file(memory_file)
        G = create_graph(entities, relations)
        
        # Comprehensive analysis
        analyze_graph(G)
        find_redundancies(entities, relations)
        
        # Create visualization
        print(f"\n🎨 Creating static visualization...")
        visualize_graph(G)
        
        print("\n" + "─"*50)
        print("📈 ANALYSIS COMPLETE:")
        print("   • Network statistics calculated")
        print("   • Redundancy patterns identified")
        print("   • High-resolution graph exported")
        print("   • Entity relationships mapped")
        print("─"*50)
        
    except FileNotFoundError:
        print(f"Memory file '{memory_file}' not found.")
        print("Please update the memory_file path in the script.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()