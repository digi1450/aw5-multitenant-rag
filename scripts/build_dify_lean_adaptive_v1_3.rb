#!/usr/bin/env ruby
# frozen_string_literal: true

# Fold the deterministic source-boundary rule into the existing Merge Context
# node. v1.2 proved that ER evidence and citation metadata survived Merge, but
# Dify emitted no message-level retriever_resources when the separate Guard node
# participated in the Merge dependency graph.

require_relative 'build_dify_lean_adaptive_v1_2'

OUTPUT_V13 = File.join(
  ROOT,
  'dify/exports/aw5-rag-lean-adaptive-v1.3-candidate-2026-08-29.yml'
)

document_v13 = YAML.load_file(OUTPUT_V12)
document_v13['app']['name'] = 'AW5-RAG Lean Adaptive v1.3 Candidate'
document_v13['app']['description'] = (
  'Lean Adaptive candidate with the deterministic source-boundary rule folded ' \
  'into Merge Context, restoring the baseline graph lineage and one fewer node.'
)

graph_v13 = document_v13.dig('workflow', 'graph')
nodes_v13 = graph_v13.fetch('nodes')
edges_v13 = graph_v13.fetch('edges')
node_by_id_v13 = nodes_v13.to_h { |node| [node['id'].to_s, node] }

guard_v13 = node_by_id_v13.fetch(GUARD_ID)
merge_v13 = node_by_id_v13.fetch(MERGE_ID)
contract_v13 = node_by_id_v13.fetch(CONTRACT_ID)

# Remove the standalone Guard and all of its graph edges.
nodes_v13.reject! { |node| node['id'].to_s == GUARD_ID }
edges_v13.reject! do |item|
  item['source'].to_s == GUARD_ID || item['target'].to_s == GUARD_ID
end

# Restore the baseline selectors. The same deterministic policy is executed
# inside Merge Context, where it filters which retrieved rows are returned.
merge_variables_v13 = merge_v13.dig('data', 'variables')
merge_variables_v13.each do |item|
  next unless %w[use_tor use_sds use_er].include?(item['variable'])

  item['value_selector'] = [ROUTE_ID, item['variable']]
end
merge_variables_v13.unshift(
  {
    'value_selector' => ['sys', 'query'],
    'value_type' => 'string',
    'variable' => 'question'
  }
)

contract_v13.dig('data', 'variables').each do |item|
  next unless %w[tor_query sds_query er_query use_er].include?(item['variable'])

  item['value_selector'] = [ROUTE_ID, item['variable']]
end

guard_code_v13 = guard_v13.dig('data', 'code').sub(
  /^def main\(/,
  'def guarded_route('
)

merge_code_v13 = <<~PYTHON
  #{guard_code_v13.rstrip}


  def main(
      question: str,
      tor_results: list,
      use_tor: str,
      sds_results: list,
      use_sds: str,
      er_results: list,
      use_er: str,
  ) -> dict:
      guarded = guarded_route(
          question,
          "route-query-present",
          "route-query-present",
          "route-query-present",
          use_tor,
          use_sds,
          use_er,
      )

      def enabled(value):
          return value is True or str(value).strip().lower() in {
              "true", "1", "yes", "y"
          }

      merged = []
      seen = set()

      for use, rows in (
          (enabled(guarded["use_tor"]), tor_results or []),
          (enabled(guarded["use_sds"]), sds_results or []),
          (enabled(guarded["use_er"]), er_results or []),
      ):
          if not use:
              continue

          for item in rows:
              if not isinstance(item, dict):
                  continue

              metadata = item.get("metadata") or {}
              key = (
                  str(metadata.get("dataset_id") or ""),
                  str(metadata.get("document_id") or ""),
                  str(metadata.get("segment_id") or ""),
                  item.get("content") or "",
              )

              if key in seen:
                  continue

              seen.add(key)
              merged.append(item)

      return {"result": merged}
PYTHON

merge_v13['data']['code'] = merge_code_v13

serialized_v13 = YAML.dump(document_v13).lines.map(&:rstrip).join("\n") + "\n"
File.write(OUTPUT_V13, serialized_v13)

ids_v13 = nodes_v13.map { |node| node['id'].to_s }
raise 'Guard node was not removed' if ids_v13.include?(GUARD_ID)
raise 'Duplicate node IDs' unless ids_v13.uniq.length == ids_v13.length
raise 'Broken edge endpoint' unless edges_v13.all? do |item|
  ids_v13.include?(item['source'].to_s) && ids_v13.include?(item['target'].to_s)
end

selectors_v13 = []
nodes_v13.each { |node| collect_selectors(node['data'] || {}, selectors_v13) }
trusted_selector_roots_v13 = %w[sys env conversation]
raise 'Broken selector reference' unless selectors_v13.all? do |item|
  trusted_selector_roots_v13.include?(item[0].to_s) ||
    ids_v13.include?(item[0].to_s)
end

nodes_v13.each do |node|
  data = node['data'] || {}
  next unless data['type'] == 'code'

  _stdout, stderr, status = Open3.capture3(
    'python3', '-c',
    'import sys; compile(sys.stdin.read(), "<dify-code>", "exec")',
    stdin_data: data['code'].to_s
  )
  raise "#{data['title']}: #{stderr}" unless status.success?
end

retrieval_edges_v13 = edges_v13.select do |item|
  RETRIEVAL_IDS.include?(item['target'].to_s)
end
raise 'Baseline retrieval fan-out changed' unless (
  retrieval_edges_v13.length == 3 &&
  retrieval_edges_v13.all? { |item| item['source'].to_s == ROUTE_ID }
)

er_fixture_v13 = run_python(
  merge_code_v13,
  "main('ตารางใดรองรับผู้ใช้ บทบาท สิทธิ์ของบทบาท และสมาชิกองค์กร?', " \
  "[{'content':'tor'}], 'false', [{'content':'sds'}], 'true', " \
  "[{'content':'er'}], 'true')"
)
raise 'Integrated ER-only Merge fixture failed' unless (
  er_fixture_v13['result'].length == 1 &&
  er_fixture_v13['result'][0]['content'] == 'er'
)

cross_fixture_v13 = run_python(
  merge_code_v13,
  "main('ข้อกำหนด Access Control ใน TOR ถูกออกแบบเป็นผู้ใช้กลุ่มใดใน SDS " \
  "และรองรับด้วยตารางใดใน ER?', [{'content':'tor'}], 'true', " \
  "[{'content':'sds'}], 'true', [{'content':'er'}], 'true')"
)
raise 'Integrated cross-source Merge fixture failed' unless (
  cross_fixture_v13['result'].map { |item| item['content'] } == %w[tor sds er]
)

puts "Built #{OUTPUT_V13}"
puts "Validated #{nodes_v13.length} nodes / #{edges_v13.length} edges"
puts "Validated #{selectors_v13.length} selectors"
puts 'Integrated Merge guard fixtures passed'
