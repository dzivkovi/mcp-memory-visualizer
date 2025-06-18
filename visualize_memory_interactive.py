#!/usr/bin/env python3
"""
Interactive Memory Visualization for Claude MCP

Creates an interactive network visualization of memory.json files from
Anthropic's Memory MCP server using PyVis. Features include:
- Draggable nodes with physics simulation
- Hover tooltips with entity details
- Color-coded entity types
- Clean, scrollable interface
- Automatic browser opening

Requires: pip install pyvis
"""

import json
from collections import Counter

try:
    from pyvis.network import Network
    import webbrowser
    import os
except ImportError:
    print("Error: Please install pyvis first:")
    print("pip install pyvis")
    exit(1)

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

def create_interactive_graph(entities, relations, output_file="memory_graph_interactive.html"):
    """Create interactive Pyvis network visualization"""
    
    # Create network with clean Neo4j-style appearance
    net = Network(
        height="800px", 
        width="100%", 
        bgcolor="#f8f9fa",  # Light background
        font_color="#2c3e50"  # Dark text for readability
    )
    
    # Configure physics for smooth, stable interactions
    net.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "stabilization": {"iterations": 100},
        "barnesHut": {
          "gravitationalConstant": -3000,
          "centralGravity": 0.2,
          "springLength": 150,
          "springConstant": 0.04,
          "damping": 0.09
        }
      }
    }
    """)
    
    # Define vibrant colors for entity types
    entity_types = list(set([e['entityType'] for e in entities]))
    colors = [
        "#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6",
        "#1abc9c", "#34495e", "#e67e22", "#8e44ad", "#16a085",
        "#2980b9", "#27ae60", "#d35400", "#c0392b", "#7f8c8d"
    ]
    color_map = dict(zip(entity_types, colors[:len(entity_types)]))
    
    # Add nodes with clean tooltips and proportional sizing
    for entity in entities:
        node_size = len(entity['observations']) * 3 + 15
        color = color_map.get(entity['entityType'], "#95a5a6")
        
        # Create readable labels
        label = entity['name']
        if len(label) > 20:
            label = label[:17] + "..."
        
        # Create clean tooltip with full text
        tooltip_lines = []
        tooltip_lines.append(f"{entity['name']}")
        tooltip_lines.append(f"Type: {entity['entityType']} | Observations: {len(entity['observations'])}")
        tooltip_lines.append("")  # Spacing
        
        # Show all observations without truncation
        if entity['observations']:
            for i, obs in enumerate(entity['observations']):
                clean_obs = obs.strip()
                tooltip_lines.append(f"{i+1}. {clean_obs}")
        
        title = "\n".join(tooltip_lines)
        
        net.add_node(
            entity['name'],
            label=label,
            title=title,
            color=color,
            size=node_size,
            font={'size': 16, 'color': '#2c3e50', 'face': 'Arial'},
            borderWidth=2,
            borderWidthSelected=4
        )
    
    # Add edges with clean styling
    for relation in relations:
        # Check if both nodes exist
        node_ids = [node['id'] for node in net.nodes]
        if relation['from'] in node_ids and relation['to'] in node_ids:
            
            # Create readable edge labels
            edge_label = relation['relationType']
            if len(edge_label) > 12:
                edge_label = edge_label[:9] + "..."
            
            # Simple connection tooltip
            connection_tooltip = f"{relation['from']} → {relation['to']}\n{relation['relationType']}"
            
            net.add_edge(
                relation['from'],
                relation['to'],
                title=connection_tooltip,
                label=edge_label,
                color={'color': '#7f8c8d', 'highlight': '#2c3e50'},
                width=2,
                font={'size': 12, 'color': '#2c3e50'}
            )
    
    # Save the visualization
    net.save_graph(output_file)
    
    # Try to open in browser
    try:
        full_path = os.path.abspath(output_file)
        webbrowser.open(f'file://{full_path}')
        print(f"\n✅ Interactive graph saved as {output_file}")
        print("🌐 Opening in your default browser...")
    except:
        print(f"\n✅ Interactive graph saved as {output_file}")
        print("📂 Open this file in your browser to view the interactive network")
    
    return net

def print_analysis(entities, relations):
    """Print the same analysis as the static version"""
    print("=== MEMORY GRAPH ANALYSIS ===")
    print(f"Total entities: {len(entities)}")
    print(f"Total relationships: {len(relations)}")
    
    # Entity types distribution
    entity_types = [e['entityType'] for e in entities]
    type_counts = Counter(entity_types)
    print("\nEntity Types:")
    for entity_type, count in type_counts.most_common():
        print(f"  {entity_type}: {count}")
    
    # Find entities with many connections
    from_counts = Counter([r['from'] for r in relations])
    to_counts = Counter([r['to'] for r in relations])
    
    # Combine counts
    total_connections = {}
    for entity in from_counts:
        total_connections[entity] = from_counts[entity] + to_counts.get(entity, 0)
    for entity in to_counts:
        if entity not in total_connections:
            total_connections[entity] = to_counts[entity]
    
    print(f"\nMost connected entities:")
    for entity, count in sorted(total_connections.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {entity}: {count} connections")
    
    print("=" * 40)

def find_redundancies(entities, relations):
    """Find potential redundancies to clean up"""
    print("\n=== REDUNDANCY ANALYSIS ===")
    
    # Find similar entity names
    names = [entity['name'] for entity in entities]
    similar_pairs = []
    for i, name1 in enumerate(names):
        for j, name2 in enumerate(names[i+1:], i+1):
            if name1.lower() in name2.lower() or name2.lower() in name1.lower():
                if name1 != name2:
                    similar_pairs.append((name1, name2))
    
    if similar_pairs:
        print("Potentially similar entities (consider merging):")
        for pair in similar_pairs:
            print(f"  - '{pair[0]}' vs '{pair[1]}'")
    
    # Find entities with very few observations
    sparse_entities = [e for e in entities if len(e['observations']) <= 1]
    if sparse_entities:
        print(f"\nEntities with minimal info (consider removing): {len(sparse_entities)}")
        for entity in sparse_entities[:5]:  # Show first 5
            print(f"  - {entity['name']}: {len(entity['observations'])} observation(s)")

def main():
    # Load memory file (demo file included, or use your own memory.json)
    memory_file = "memory.json"
    
    try:
        entities, relations = load_memory_file(memory_file)
        
        # Print analysis (same as static version)
        print_analysis(entities, relations)
        find_redundancies(entities, relations)
        
        # Create interactive visualization
        print("\n🎨 Creating interactive visualization...")
        create_interactive_graph(entities, relations)
        
        print("\n" + "─"*50)
        print("🖱️  INTERACTIVE FEATURES:")
        print("   • Drag nodes to reorganize the layout")
        print("   • Hover over nodes for detailed information")
        print("   • Click and drag to pan around the graph")
        print("   • Scroll to zoom in and out")
        print("   • Physics simulation for natural movement")
        print("─"*50)
        
    except FileNotFoundError:
        print(f"Memory file '{memory_file}' not found.")
        print("Please update the memory_file path in the script.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()