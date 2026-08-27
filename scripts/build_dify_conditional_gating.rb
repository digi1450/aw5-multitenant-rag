#!/usr/bin/env ruby
# frozen_string_literal: true

# Build an import-as-new Dify DSL that conditionally gates TOR/SDS/ER retrieval.
# The verified baseline is read-only; this script writes a separate test export.

require 'yaml'
require 'fileutils'

ROOT = File.expand_path('..', __dir__)
SOURCE = File.join(ROOT, 'dify/exports/aw5-rag-source-routing-final-2026-08-25.yml')
OUTPUT = File.join(ROOT, 'dify/exports/aw5-rag-conditional-gating-test-2026-08-27.yml')

ROUTE_ID = '1787595925652'
MERGE_ID = '1787596247169'
LLM2_ID = '1787022382039'
ANSWER_ID = 'answer_node'

SOURCES = {
  'tor' => {
    'flag' => 'use_tor',
    'retriever_id' => '1787596029280',
    'gate_id' => '1790000000001',
    'empty_id' => '1790000000002',
    'aggregator_id' => '1790000000003',
    'condition_id' => '2790000000001',
    'group_id' => '3790000000001',
    'y' => 390.0
  },
  'sds' => {
    'flag' => 'use_sds',
    'retriever_id' => '1787596169909',
    'gate_id' => '1790000000011',
    'empty_id' => '1790000000012',
    'aggregator_id' => '1790000000013',
    'condition_id' => '2790000000011',
    'group_id' => '3790000000011',
    'y' => 690.0
  },
  'er' => {
    'flag' => 'use_er',
    'retriever_id' => '1787596201775',
    'gate_id' => '1790000000021',
    'empty_id' => '1790000000022',
    'aggregator_id' => '1790000000023',
    'condition_id' => '2790000000021',
    'group_id' => '3790000000021',
    'y' => 990.0
  }
}.freeze

def edge(source, source_type, source_handle, target, target_type)
  {
    'data' => {
      'isInIteration' => false,
      'isInLoop' => false,
      'sourceType' => source_type,
      'targetType' => target_type
    },
    'id' => "#{source}-#{source_handle}-#{target}-target",
    'selected' => false,
    'source' => source,
    'sourceHandle' => source_handle,
    'target' => target,
    'targetHandle' => 'target',
    'type' => 'custom',
    'zIndex' => 0
  }
end

def shell(source, title, type, x, y, height = 100)
  {
    'data' => {
      'desc' => '',
      'selected' => false,
      'title' => title,
      'type' => type
    },
    'height' => height,
    'id' => source,
    'position' => {'x' => x, 'y' => y},
    'positionAbsolute' => {'x' => x, 'y' => y},
    'selected' => false,
    'sourcePosition' => 'right',
    'targetPosition' => 'left',
    'type' => 'custom',
    'width' => 242,
    'zIndex' => 0
  }
end

def gate_node(config, label)
  node = shell(config['gate_id'], "Gate #{label}", 'if-else', 800.0, config['y'], 126)
  node['data'].merge!({
    '_targetBranches' => [
      {'id' => 'true', 'name' => 'IF'},
      {'id' => 'false', 'name' => 'ELSE'}
    ],
    'cases' => [{
      'case_id' => 'true',
      'conditions' => [{
        'comparison_operator' => 'is',
        'id' => config['condition_id'],
        'value' => 'true',
        'varType' => 'string',
        'variable_selector' => [ROUTE_ID, config['flag']]
      }],
      'logical_operator' => 'and'
    }],
    'logical_operator' => 'and'
  })
  node
end

def empty_node(config, label)
  node = shell(config['empty_id'], "Empty #{label} Results", 'code', 1110.0, config['y'] + 118.0, 54)
  node['data'].merge!({
    'code' => "def main() -> dict:\n    return {\"result\": []}\n",
    'code_language' => 'python3',
    'outputs' => {
      'result' => {'children' => nil, 'type' => 'array[object]'}
    },
    'variables' => []
  })
  node
end

def aggregator_node(config, label)
  variables = [
    [config['retriever_id'], 'result'],
    [config['empty_id'], 'result']
  ]
  node = shell(config['aggregator_id'], "Select #{label} Results", 'variable-aggregator', 1415.0, config['y'] + 45.0, 129)
  node['data'].merge!({
    'advanced_settings' => {
      'group_enabled' => false,
      'groups' => [{
        'groupId' => config['group_id'],
        'group_name' => 'Group1',
        'output_type' => 'array[object]',
        'variables' => variables.map(&:dup)
      }]
    },
    'output_type' => 'array[object]',
    'variables' => variables.map(&:dup)
  })
  node
end

def move(node, x, y)
  node['position'] = {'x' => x, 'y' => y}
  node['positionAbsolute'] = {'x' => x, 'y' => y}
end

document = YAML.load_file(SOURCE)
document.dig('app', 'name').replace('AW5-RAG Conditional Gating Test')
graph = document.dig('workflow', 'graph')
nodes = graph.fetch('nodes')
edges = graph.fetch('edges')

retriever_ids = SOURCES.values.map { |config| config['retriever_id'] }
edges.reject! do |item|
  (item['source'] == ROUTE_ID && retriever_ids.include?(item['target'])) ||
    (retriever_ids.include?(item['source']) && item['target'] == MERGE_ID)
end

node_by_id = nodes.to_h { |node| [node['id'].to_s, node] }

SOURCES.each do |key, config|
  label = key.upcase
  retriever = node_by_id.fetch(config['retriever_id'])
  move(retriever, 1110.0, config['y'])

  nodes << gate_node(config, label)
  nodes << empty_node(config, label)
  nodes << aggregator_node(config, label)

  edges << edge(ROUTE_ID, 'code', 'source', config['gate_id'], 'if-else')
  edges << edge(config['gate_id'], 'if-else', 'true', config['retriever_id'], 'knowledge-retrieval')
  edges << edge(config['gate_id'], 'if-else', 'false', config['empty_id'], 'code')
  edges << edge(config['retriever_id'], 'knowledge-retrieval', 'source', config['aggregator_id'], 'variable-aggregator')
  edges << edge(config['empty_id'], 'code', 'source', config['aggregator_id'], 'variable-aggregator')
  edges << edge(config['aggregator_id'], 'variable-aggregator', 'source', MERGE_ID, 'code')
end

merge = node_by_id.fetch(MERGE_ID)
merge_variables = merge.dig('data', 'variables')
SOURCES.each_value do |config|
  variable = merge_variables.find { |item| item['variable'] == "#{config['flag'].delete_prefix('use_')}_results" }
  raise "Missing Merge Context variable for #{config['flag']}" unless variable

  variable['value_selector'] = [config['aggregator_id'], 'output']
  variable['value_type'] = 'array[object]'
end

move(merge, 1720.0, 690.0)
move(node_by_id.fetch(LLM2_ID), 2025.0, 690.0)
move(node_by_id.fetch(ANSWER_ID), 2330.0, 690.0)

node_ids = nodes.map { |node| node['id'].to_s }
raise 'Duplicate node IDs' unless node_ids.uniq.length == node_ids.length
raise "Expected 18 nodes, found #{nodes.length}" unless nodes.length == 18
raise "Expected 22 edges, found #{edges.length}" unless edges.length == 22
edges.each do |item|
  raise "Unknown edge source #{item['source']}" unless node_ids.include?(item['source'].to_s)
  raise "Unknown edge target #{item['target']}" unless node_ids.include?(item['target'].to_s)
end

SOURCES.each_value do |config|
  direct = edges.any? { |item| item['source'] == ROUTE_ID && item['target'] == config['retriever_id'] }
  raise "Ungated retrieval remains for #{config['flag']}" if direct

  handles = edges
            .select { |item| item['source'] == config['gate_id'] }
            .map { |item| item['sourceHandle'] }
            .sort
  raise "Gate branches invalid for #{config['flag']}" unless handles == %w[false true]

  aggregator = nodes.find { |node| node['id'] == config['aggregator_id'] }
  expected_inputs = [[config['retriever_id'], 'result'], [config['empty_id'], 'result']]
  raise "Aggregator inputs invalid for #{config['flag']}" unless aggregator.dig('data', 'variables') == expected_inputs

  merge_variable = merge_variables.find { |item| item['variable'] == "#{config['flag'].delete_prefix('use_')}_results" }
  expected_output = [config['aggregator_id'], 'output']
  raise "Merge selector invalid for #{config['flag']}" unless merge_variable['value_selector'] == expected_output
end

FileUtils.mkdir_p(File.dirname(OUTPUT))
File.write(OUTPUT, YAML.dump(document, line_width: -1))
puts OUTPUT
