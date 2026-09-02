#!/usr/bin/env ruby
# frozen_string_literal: true

# Add a deterministic source-boundary guard to Lean Adaptive v1 after a live
# ER-01 run demonstrated LLM 1 over-routing to SDS. The live Dify app is not
# modified or published by this script.

require_relative 'build_dify_lean_adaptive_v1'

OUTPUT_V11 = File.join(
  ROOT,
  'dify/exports/aw5-rag-lean-adaptive-v1.1-candidate-2026-08-29.yml'
)
GUARD_ID = '1787838414311'
RETRIEVAL_IDS = %w[1787596029280 1787596169909 1787596201775].freeze

document_v11 = YAML.load_file(OUTPUT)
template_v11 = YAML.load_file(TEMPLATE)
document_v11['app']['name'] = 'AW5-RAG Lean Adaptive v1.1 Candidate'
document_v11['app']['description'] = (
  'Lean Adaptive v1 plus a deterministic source-boundary guard after a live ' \
  'ER-01 run demonstrated LLM 1 over-routing and an unrelated SDS citation.'
)

graph_v11 = document_v11.dig('workflow', 'graph')
nodes_v11 = graph_v11.fetch('nodes')
edges_v11 = graph_v11.fetch('edges')
node_by_id_v11 = nodes_v11.to_h { |node| [node['id'].to_s, node] }
template_nodes_v11 = template_v11.dig('workflow', 'graph', 'nodes')
template_by_id_v11 = template_nodes_v11.to_h { |node| [node['id'].to_s, node] }

# Make room between Route Queries and the unchanged retrieval layer.
nodes_v11.each do |node|
  position = node['position'] || {}
  next unless position['x'].to_f >= 797

  %w[position positionAbsolute].each do |key|
    node[key] ||= {}
    node[key]['x'] = node[key]['x'].to_f + 300
  end
end

guard = deep_copy(template_by_id_v11.fetch(GUARD_ID))
guard['position'] = {'x' => 795, 'y' => 534}
guard['positionAbsolute'] = {'x' => 795, 'y' => 534}
guard['data']['title'] = 'LEAN ROUTE GUARD'
nodes_v11 << guard

# Keep the baseline retrieval queries non-empty in v1.1. All three retrievers still
# execute as in the control; the guard determines which results enter Merge Context.
# Conditional retrieval is a separate v1.2 experiment after source-boundary proof.
merge_variables = node_by_id_v11.fetch(MERGE_ID).dig('data', 'variables')
merge_variables.each do |item|
  next unless %w[use_tor use_sds use_er].include?(item['variable'])

  item['value_selector'] = [GUARD_ID, item['variable']]
end

contract_variables = node_by_id_v11.fetch(CONTRACT_ID).dig('data', 'variables')
contract_variables.each do |item|
  next unless %w[tor_query sds_query er_query use_er].include?(item['variable'])

  item['value_selector'] = [GUARD_ID, item['variable']]
end

# Replace only the Route Queries -> retrieval fan-out.
edges_v11.reject! do |item|
  item['source'].to_s == ROUTE_ID && RETRIEVAL_IDS.include?(item['target'].to_s)
end
edges_v11 << edge(ROUTE_ID, 'code', GUARD_ID, 'code')
RETRIEVAL_IDS.each do |target|
  edges_v11 << edge(GUARD_ID, 'code', target, 'knowledge-retrieval')
end

serialized_v11 = YAML.dump(document_v11).lines.map(&:rstrip).join("\n") + "\n"
File.write(OUTPUT_V11, serialized_v11)

ids_v11 = nodes_v11.map { |node| node['id'].to_s }
raise 'Duplicate node IDs' unless ids_v11.uniq.length == ids_v11.length
raise 'Broken edge endpoint' unless edges_v11.all? do |item|
  ids_v11.include?(item['source'].to_s) && ids_v11.include?(item['target'].to_s)
end

selectors_v11 = []
nodes_v11.each { |node| collect_selectors(node['data'] || {}, selectors_v11) }
trusted_selector_roots_v11 = %w[sys env conversation]
raise 'Broken selector reference' unless selectors_v11.all? do |item|
  trusted_selector_roots_v11.include?(item[0].to_s) ||
    ids_v11.include?(item[0].to_s)
end

indegree_v11 = ids_v11.to_h { |id| [id, 0] }
adjacency_v11 = Hash.new { |hash, key| hash[key] = [] }
edges_v11.each do |item|
  source = item['source'].to_s
  target = item['target'].to_s
  adjacency_v11[source] << target
  indegree_v11[target] += 1
end
queue_v11 = indegree_v11.select { |_id, count| count.zero? }.keys
visited_v11 = []
until queue_v11.empty?
  node_id = queue_v11.shift
  visited_v11 << node_id
  adjacency_v11[node_id].each do |target|
    indegree_v11[target] -= 1
    queue_v11 << target if indegree_v11[target].zero?
  end
end
raise 'Graph contains a cycle' unless visited_v11.length == ids_v11.length

nodes_v11.each do |node|
  data = node['data'] || {}
  next unless data['type'] == 'code'

  _stdout, stderr, status = Open3.capture3(
    'python3', '-c',
    'import sys; compile(sys.stdin.read(), "<dify-code>", "exec")',
    stdin_data: data['code'].to_s
  )
  raise "#{data['title']}: #{stderr}" unless status.success?
end

guard_code = guard.dig('data', 'code')

er_route = run_python(
  guard_code,
  "main('ตารางใดรองรับผู้ใช้ บทบาท สิทธิ์ของบทบาท และสมาชิกองค์กร?', " \
  "'ผู้ใช้งานหลัก บทบาท สิทธิ์', 'ผู้ใช้งานหลัก บทบาท สิทธิ์', " \
  "'RBAC UM_USER UM_ROLE UM_USER_ROLE UM_FUNCTION UM_ROLE_FUNCTION " \
  "UM_USER_ORG', 'false', 'true', 'true')"
)
raise 'ER-only guard fixture failed' unless (
  er_route['use_tor'] == 'false' &&
  er_route['use_sds'] == 'false' &&
  er_route['use_er'] == 'true' &&
  er_route['guard_reason'] == 'database_only'
)

cross_route = run_python(
  guard_code,
  "main('ข้อกำหนด Access Control ใน TOR ถูกออกแบบเป็นผู้ใช้กลุ่มใดใน SDS " \
  "และรองรับด้วยตารางใดใน ER?', 'TOR Access Control', 'SDS user groups', " \
  "'ER RBAC UM_USER', 'true', 'true', 'true')"
)
raise 'Explicit cross-source guard fixture failed' unless (
  cross_route['use_tor'] == 'true' &&
  cross_route['use_sds'] == 'true' &&
  cross_route['use_er'] == 'true'
)

tor_route = run_python(
  guard_code,
  "main('TOR ข้อ 14 กำหนดเรื่องความปลอดภัยและ Audit Log อย่างไร?', " \
  "'TOR ข้อ 14 Audit Log', 'Audit Log', '', 'true', 'true', 'false')"
)
raise 'Explicit TOR-only guard fixture failed' unless (
  tor_route['use_tor'] == 'true' &&
  tor_route['use_sds'] == 'false' &&
  tor_route['use_er'] == 'false'
)

provider_route = run_python(
  guard_code,
  "main('ระบบ Production ใช้ AWS, Google Cloud หรือ Azure?', " \
  "'production hosting', 'cloud offsite storage', '', 'true', 'true', 'false')"
)
raise 'Ambiguous provider route should preserve LLM route' unless (
  provider_route['use_tor'] == 'true' &&
  provider_route['use_sds'] == 'true' &&
  provider_route['use_er'] == 'false' &&
  provider_route['guard_reason'] == 'keep_llm_route'
)

puts "Built #{OUTPUT_V11}"
puts "Validated #{nodes_v11.length} nodes / #{edges_v11.length} edges"
puts "Validated #{selectors_v11.length} selectors and acyclic graph"
puts 'Lean Route Guard fixtures passed'
