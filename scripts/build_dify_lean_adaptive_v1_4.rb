#!/usr/bin/env ruby
# frozen_string_literal: true

# Normalize the deterministic source boundary inside the existing Route Queries
# node while leaving Merge Context and the full graph identical to v1. This tests
# the smallest route correction that preserves the last citation-positive shape.

require_relative 'build_dify_lean_adaptive_v1_2'

OUTPUT_V14 = File.join(
  ROOT,
  'dify/exports/aw5-rag-lean-adaptive-v1.4-candidate-2026-08-29.yml'
)

document_v14 = YAML.load_file(OUTPUT)
guard_document_v14 = YAML.load_file(OUTPUT_V12)
document_v14['app']['name'] = 'AW5-RAG Lean Adaptive v1.4 Candidate'
document_v14['app']['description'] = (
  'Lean Adaptive v1 with deterministic source normalization folded into the ' \
  'existing Route Queries node; graph and Merge Context remain identical to v1.'
)

graph_v14 = document_v14.dig('workflow', 'graph')
nodes_v14 = graph_v14.fetch('nodes')
edges_v14 = graph_v14.fetch('edges')
route_v14 = nodes_v14.find { |node| node['id'].to_s == ROUTE_ID }
raise 'Route Queries node missing' unless route_v14

guard_v14 = guard_document_v14.dig('workflow', 'graph', 'nodes').find do |node|
  node['id'].to_s == GUARD_ID
end
raise 'Guard policy source missing' unless guard_v14

original_route_code_v14 = route_v14.dig('data', 'code').sub(
  /^def main\(/,
  'def normalize_route('
)
guard_code_v14 = guard_v14.dig('data', 'code').sub(
  /^def main\(/,
  'def guarded_route('
)

route_v14['data']['variables'].unshift(
  {
    'value_selector' => ['sys', 'query'],
    'value_type' => 'string',
    'variable' => 'question'
  }
)

route_code_v14 = <<~PYTHON
  #{original_route_code_v14.rstrip}


  #{guard_code_v14.rstrip}


  def main(question: str, route: dict) -> dict:
      normalized = normalize_route(route)
      guarded = guarded_route(
          question,
          normalized["tor_query"],
          normalized["sds_query"],
          normalized["er_query"],
          normalized["use_tor"],
          normalized["use_sds"],
          normalized["use_er"],
      )

      # Keep retrieval queries populated because the v1 graph executes all three
      # retrieval nodes. Guarded flags determine which results enter Merge.
      return {
          "tor_query": normalized["tor_query"],
          "sds_query": normalized["sds_query"],
          "er_query": normalized["er_query"],
          "use_tor": guarded["use_tor"],
          "use_sds": guarded["use_sds"],
          "use_er": guarded["use_er"],
          "guard_reason": guarded["guard_reason"],
      }
PYTHON

route_v14['data']['code'] = route_code_v14
route_v14['data']['outputs']['guard_reason'] = {
  'children' => nil,
  'type' => 'string'
}

serialized_v14 = YAML.dump(document_v14).lines.map(&:rstrip).join("\n") + "\n"
File.write(OUTPUT_V14, serialized_v14)

ids_v14 = nodes_v14.map { |node| node['id'].to_s }
raise 'Duplicate node IDs' unless ids_v14.uniq.length == ids_v14.length
raise 'Broken edge endpoint' unless edges_v14.all? do |item|
  ids_v14.include?(item['source'].to_s) && ids_v14.include?(item['target'].to_s)
end

selectors_v14 = []
nodes_v14.each { |node| collect_selectors(node['data'] || {}, selectors_v14) }
trusted_selector_roots_v14 = %w[sys env conversation]
raise 'Broken selector reference' unless selectors_v14.all? do |item|
  trusted_selector_roots_v14.include?(item[0].to_s) ||
    ids_v14.include?(item[0].to_s)
end

nodes_v14.each do |node|
  data = node['data'] || {}
  next unless data['type'] == 'code'

  _stdout, stderr, status = Open3.capture3(
    'python3', '-c',
    'import sys; compile(sys.stdin.read(), "<dify-code>", "exec")',
    stdin_data: data['code'].to_s
  )
  raise "#{data['title']}: #{stderr}" unless status.success?
end

baseline_v14 = YAML.load_file(OUTPUT)
baseline_graph_v14 = baseline_v14.dig('workflow', 'graph')
baseline_merge_v14 = baseline_graph_v14.fetch('nodes').find do |node|
  node['id'].to_s == MERGE_ID
end
candidate_merge_v14 = nodes_v14.find { |node| node['id'].to_s == MERGE_ID }
raise 'Merge Context changed from citation-positive v1' unless (
  candidate_merge_v14['data'] == baseline_merge_v14['data']
)

baseline_edges_v14 = baseline_graph_v14.fetch('edges').map do |item|
  [item['source'].to_s, item['target'].to_s, item['sourceHandle'], item['targetHandle']]
end.sort
candidate_edges_v14 = edges_v14.map do |item|
  [item['source'].to_s, item['target'].to_s, item['sourceHandle'], item['targetHandle']]
end.sort
raise 'Graph edges changed from citation-positive v1' unless (
  candidate_edges_v14 == baseline_edges_v14
)

er_fixture_v14 = run_python(
  route_code_v14,
  "main('ตารางใดรองรับผู้ใช้ บทบาท สิทธิ์ของบทบาท และสมาชิกองค์กร?', " \
  "{'tor_query':'ผู้ใช้', 'sds_query':'ผู้ใช้', " \
  "'er_query':'RBAC UM_USER UM_ROLE UM_USER_ROLE UM_FUNCTION " \
  "UM_ROLE_FUNCTION UM_USER_ORG', 'use_tor':False, " \
  "'use_sds':True, 'use_er':True})"
)
raise 'Integrated Route ER-only fixture failed' unless (
  er_fixture_v14['use_tor'] == 'false' &&
  er_fixture_v14['use_sds'] == 'false' &&
  er_fixture_v14['use_er'] == 'true' &&
  er_fixture_v14['sds_query'] == 'ผู้ใช้'
)

cross_fixture_v14 = run_python(
  route_code_v14,
  "main('ข้อกำหนด Access Control ใน TOR ถูกออกแบบเป็นผู้ใช้กลุ่มใดใน SDS " \
  "และรองรับด้วยตารางใดใน ER?', {'tor_query':'TOR Access Control', " \
  "'sds_query':'SDS groups', 'er_query':'ER RBAC', 'use_tor':True, " \
  "'use_sds':True, 'use_er':True})"
)
raise 'Integrated Route cross-source fixture failed' unless (
  cross_fixture_v14['use_tor'] == 'true' &&
  cross_fixture_v14['use_sds'] == 'true' &&
  cross_fixture_v14['use_er'] == 'true'
)

puts "Built #{OUTPUT_V14}"
puts "Validated #{nodes_v14.length} nodes / #{edges_v14.length} edges"
puts "Validated #{selectors_v14.length} selectors"
puts 'Route fixtures and exact v1 Merge/edge parity passed'
