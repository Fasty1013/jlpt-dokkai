/**
 * JLPT Dokkai Master - Dependency Graph & Cycle Detection Tool
 * Analyzes ES Module imports in static/js and verifies acyclic structure (DAG).
 */

const fs = require('fs');
const path = require('path');

function walk(dir) {
  let results = [];
  if (!fs.existsSync(dir)) return results;
  fs.readdirSync(dir).forEach(file => {
    const full = path.join(dir, file);
    if (fs.statSync(full).isDirectory()) {
      if (file !== 'node_modules') results = results.concat(walk(full));
    } else if (file.endsWith('.js')) {
      results.push(full);
    }
  });
  return results;
}

function analyzeGraph(baseDir = 'static/js') {
  const files = walk(baseDir);
  const graph = {};

  files.forEach(f => {
    const norm = f.replace(/\\/g, '/');
    graph[norm] = [];
    const content = fs.readFileSync(f, 'utf8');
    const importRegex = /(?:import\s+(?:[\w*\s{},]*)\s+from\s+['"]([^'"]+)['"])|(?:import\s*['"]([^'"]+)['"])/g;
    let match;
    while ((match = importRegex.exec(content)) !== null) {
      const imp = match[1] || match[2];
      if (imp && imp.startsWith('.')) {
        let resolved = path.normalize(path.join(path.dirname(norm), imp)).replace(/\\/g, '/');
        if (!resolved.endsWith('.js')) resolved += '.js';
        graph[norm].push(resolved);
      }
    }
  });

  const visited = {};
  const recStack = {};
  const cycles = [];

  function isCyclic(node, pathArr = []) {
    visited[node] = true;
    recStack[node] = true;
    pathArr.push(node);

    for (const neighbor of (graph[node] || [])) {
      if (!visited[neighbor]) {
        isCyclic(neighbor, [...pathArr]);
      } else if (recStack[neighbor]) {
        cycles.push([...pathArr, neighbor].join(' -> '));
      }
    }
    recStack[node] = false;
  }

  for (const node of Object.keys(graph)) {
    if (!visited[node]) {
      isCyclic(node);
    }
  }

  return { graph, cycles, totalModules: Object.keys(graph).length };
}

if (require.main === module) {
  const result = analyzeGraph();
  console.log(`Total ES modules analyzed: ${result.totalModules}`);
  if (result.cycles.length > 0) {
    console.error(`FAILURE: Detected ${result.cycles.length} circular dependencies:`);
    result.cycles.forEach(c => console.error(`  - ${c}`));
    process.exit(1);
  } else {
    console.log('SUCCESS: Dependency graph is a valid Directed Acyclic Graph (DAG) with 0 cycles.');
  }
}

module.exports = { analyzeGraph };

