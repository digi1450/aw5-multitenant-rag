#!/usr/bin/env ruby
# frozen_string_literal: true

# Preserve baseline retrieval-edge provenance while keeping the deterministic
# source boundary at Merge Context. This follows two v1.1 ER-01 runs where answer
# and guarded routing passed but Dify emitted no citations.

require_relative 'build_dify_lean_adaptive_v1_1'

OUTPUT_V12 = File.join(
  ROOT,
  'dify/exports/aw5-rag-lean-adaptive-v1.2-candidate-2026-08-29.yml'
)

document_v12 = YAML.load_file(OUTPUT_V11)
document_v12['app']['name'] = 'AW5-RAG Lean Adaptive v1.2 Candidate'
document_v12['app']['description'] = (
  'Lean Adaptive v1.1 with baseline Route Queries to Retrieval edges restored ' \
  'for Dify citation provenance; the Guard independently gates Merge Context.'
)

graph_v12 = document_v12.dig('workflow', 'graph')
nodes_v12 = graph_v12.fetch('nodes')
edges_v12 = graph_v12.fetch('edges')

# Restore the exact baseline retrieval fan-out. Guard remains a parallel child of
# Route Queries and a direct dependency of Merge Context, whose use_* selectors
# already reference the Guard outputs.
edges_v12.reject! do |item|
  item['source'].to_s == GUARD_ID && RETRIEVAL_IDS.include?(item['target'].to_s)
end
RETRIEVAL_IDS.each do |target|
  edges_v12 << edge(ROUTE_ID, 'code', target, 'knowledge-retrieval')
end
edges_v12 << edge(GUARD_ID, 'code', MERGE_ID, 'code')

serialized_v12 = YAML.dump(document_v12).lines.map(&:rstrip).join("\n") + "\n"
File.write(OUTPUT_V12, serialized_v12)

ids_v12 = nodes_v12.map { |node| node['id'].to_s }
raise 'Duplicate node IDs' unless ids_v12.uniq.length == ids_v12.length
raise 'Broken edge endpoint' unless edges_v12.all? do |item|
  ids_v12.include?(item['source'].to_s) && ids_v12.include?(item['target'].to_s)
end

selectors_v12 = []
nodes_v12.each { |node| collect_selectors(node['data'] || {}, selectors_v12) }
trusted_selector_roots_v12 = %w[sys env conversation]
raise 'Broken selector reference' unless selectors_v12.all? do |item|
  trusted_selector_roots_v12.include?(item[0].to_s) ||
    ids_v12.include?(item[0].to_s)
end

indegree_v12 = ids_v12.to_h { |id| [id, 0] }
adjacency_v12 = Hash.new { |hash, key| hash[key] = [] }
edges_v12.each do |item|
  source = item['source'].to_s
  target = item['target'].to_s
  adjacency_v12[source] << target
  indegree_v12[target] += 1
end
queue_v12 = indegree_v12.select { |_id, count| count.zero? }.keys
visited_v12 = []
until queue_v12.empty?
  node_id = queue_v12.shift
  visited_v12 << node_id
  adjacency_v12[node_id].each do |target|
    indegree_v12[target] -= 1
    queue_v12 << target if indegree_v12[target].zero?
  end
end
raise 'Graph contains a cycle' unless visited_v12.length == ids_v12.length

nodes_v12.each do |node|
  data = node['data'] || {}
  next unless data['type'] == 'code'

  _stdout, stderr, status = Open3.capture3(
    'python3', '-c',
    'import sys; compile(sys.stdin.read(), "<dify-code>", "exec")',
    stdin_data: data['code'].to_s
  )
  raise "#{data['title']}: #{stderr}" unless status.success?
end

retrieval_edges = edges_v12.select do |item|
  RETRIEVAL_IDS.include?(item['target'].to_s)
end
raise 'Baseline retrieval provenance was not restored' unless (
  retrieval_edges.length == 3 &&
  retrieval_edges.all? { |item| item['source'].to_s == ROUTE_ID }
)

guard_merge = edges_v12.any? do |item|
  item['source'].to_s == GUARD_ID && item['target'].to_s == MERGE_ID
end
raise 'Guard is not a Merge dependency' unless guard_merge

puts "Built #{OUTPUT_V12}"
puts "Validated #{nodes_v12.length} nodes / #{edges_v12.length} edges"
puts "Validated #{selectors_v12.length} selectors and acyclic graph"
puts 'Baseline retrieval provenance and guarded Merge dependency passed'
