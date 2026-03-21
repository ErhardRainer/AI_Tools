/**
 * Tests für n8n Custom Nodes (LlmClient, ImageGen).
 *
 * Keine echten API-Calls — nur strukturelle und Metadaten-Tests
 * auf den kompilierten JS-Dateien.
 *
 * Ausführen: node n8n/tests/test_nodes.js
 */

'use strict';

const assert = require('node:assert/strict');
const path = require('node:path');

// ── Hilfsfunktionen ──────────────────────────────────────────────────────────

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  ✓ ${name}`);
    passed++;
  } catch (err) {
    console.error(`  ✗ ${name}`);
    console.error(`    → ${err.message}`);
    failed++;
  }
}

function section(title) {
  console.log(`\n${title}`);
  console.log('─'.repeat(title.length));
}

// ── Imports ──────────────────────────────────────────────────────────────────

const distDir = path.join(__dirname, '..', 'dist');

const { LlmClientNode }        = require(path.join(distDir, 'nodes', 'LlmClient', 'LlmClient.node.js'));
const { ImageGenNode }         = require(path.join(distDir, 'nodes', 'ImageGen',   'ImageGen.node.js'));
const { MediaApiCredentials }  = require(path.join(distDir, 'credentials',          'MediaApiCredentials.js'));

// ── MediaApiCredentials ───────────────────────────────────────────────────────

section('MediaApiCredentials');

const creds = new MediaApiCredentials();

test('name ist "mediaApiCredentials"', () => {
  assert.equal(creds.name, 'mediaApiCredentials');
});

test('displayName enthält "Media API"', () => {
  assert.ok(creds.displayName.includes('Media API'));
});

test('hat baseUrl-Property', () => {
  const prop = creds.properties.find(p => p.name === 'baseUrl');
  assert.ok(prop, 'baseUrl property nicht gefunden');
  assert.equal(prop.default, 'http://localhost:8000');
});

test('hat apiKey-Property (optional)', () => {
  const prop = creds.properties.find(p => p.name === 'apiKey');
  assert.ok(prop, 'apiKey property nicht gefunden');
  assert.equal(prop.default, '');
});

test('test-Request zeigt auf /health', () => {
  assert.ok(creds.test.request.url.includes('/health'));
});

// ── LlmClientNode ─────────────────────────────────────────────────────────────

section('LlmClientNode');

const llmNode = new LlmClientNode();
const llmDesc = llmNode.description;

test('name ist "llmClient"', () => {
  assert.equal(llmDesc.name, 'llmClient');
});

test('displayName enthält "LLM"', () => {
  assert.ok(llmDesc.displayName.includes('LLM'));
});

test('hat genau eine Credential: mediaApiCredentials', () => {
  assert.equal(llmDesc.credentials.length, 1);
  assert.equal(llmDesc.credentials[0].name, 'mediaApiCredentials');
});

test('Provider-Dropdown enthält alle 8 Provider', () => {
  const providerProp = llmDesc.properties.find(p => p.name === 'provider');
  assert.ok(providerProp, 'provider property nicht gefunden');
  const values = providerProp.options.map(o => o.value);
  for (const p of ['openai', 'claude', 'gemini', 'grok', 'kimi', 'deepseek', 'groq', 'mistral']) {
    assert.ok(values.includes(p), `Provider '${p}' fehlt`);
  }
});

test('hat system, context, task Properties', () => {
  const names = llmDesc.properties.map(p => p.name);
  for (const n of ['system', 'context', 'task']) {
    assert.ok(names.includes(n), `Property '${n}' fehlt`);
  }
});

test('hat outputFormat-Property mit plain und json', () => {
  const prop = llmDesc.properties.find(p => p.name === 'outputFormat');
  assert.ok(prop, 'outputFormat property nicht gefunden');
  const vals = prop.options.map(o => o.value);
  assert.ok(vals.includes('plain'));
  assert.ok(vals.includes('json'));
});

test('hat preset-Property', () => {
  const names = llmDesc.properties.map(p => p.name);
  assert.ok(names.includes('preset'));
});

test('inputs und outputs sind "main"', () => {
  assert.equal(llmDesc.inputs[0], 'main');
  assert.equal(llmDesc.outputs[0], 'main');
});

test('execute ist eine async-Funktion', () => {
  assert.ok(typeof llmNode.execute === 'function');
  // Async-Funktionen sind Instanzen von AsyncFunction
  const AsyncFunction = (async () => {}).constructor;
  assert.ok(llmNode.execute instanceof AsyncFunction);
});

// ── ImageGenNode ──────────────────────────────────────────────────────────────

section('ImageGenNode');

const imgNode = new ImageGenNode();
const imgDesc = imgNode.description;

test('name ist "imageGen"', () => {
  assert.equal(imgDesc.name, 'imageGen');
});

test('displayName enthält "Image"', () => {
  assert.ok(imgDesc.displayName.toLowerCase().includes('image'));
});

test('hat genau eine Credential: mediaApiCredentials', () => {
  assert.equal(imgDesc.credentials.length, 1);
  assert.equal(imgDesc.credentials[0].name, 'mediaApiCredentials');
});

test('Provider-Dropdown enthält alle 9 Provider', () => {
  const providerProp = imgDesc.properties.find(p => p.name === 'provider');
  assert.ok(providerProp, 'provider property nicht gefunden');
  const values = providerProp.options.map(o => o.value);
  for (const p of ['openai', 'google', 'stability', 'fal', 'ideogram', 'leonardo', 'firefly', 'auto1111', 'ollamadiffuser']) {
    assert.ok(values.includes(p), `Provider '${p}' fehlt`);
  }
});

test('hat prompt-Property', () => {
  const names = imgDesc.properties.map(p => p.name);
  assert.ok(names.includes('prompt'), 'prompt property fehlt');
});

test('hat n-Property (Anzahl Bilder)', () => {
  const prop = imgDesc.properties.find(p => p.name === 'n');
  assert.ok(prop, 'n property nicht gefunden');
  assert.equal(prop.default, 1);
});

test('hat aspectRatio-Property mit 1:1 als Standard', () => {
  const prop = imgDesc.properties.find(p => p.name === 'aspectRatio');
  assert.ok(prop, 'aspectRatio property nicht gefunden');
  assert.equal(prop.default, '1:1');
});

test('hat quality-Property nur für openai', () => {
  const prop = imgDesc.properties.find(p => p.name === 'quality');
  assert.ok(prop, 'quality property nicht gefunden');
  assert.ok(prop.displayOptions?.show?.provider?.includes('openai'));
});

test('hat imageOutput-Property mit 3 Optionen', () => {
  const prop = imgDesc.properties.find(p => p.name === 'imageOutput');
  assert.ok(prop, 'imageOutput property nicht gefunden');
  assert.equal(prop.options.length, 3);
  const vals = prop.options.map(o => o.value);
  assert.ok(vals.includes('both') && vals.includes('url') && vals.includes('b64'));
});

test('inputs und outputs sind "main"', () => {
  assert.equal(imgDesc.inputs[0], 'main');
  assert.equal(imgDesc.outputs[0], 'main');
});

test('execute ist eine async-Funktion', () => {
  assert.ok(typeof imgNode.execute === 'function');
  const AsyncFunction = (async () => {}).constructor;
  assert.ok(imgNode.execute instanceof AsyncFunction);
});

// ── Zusammenfassung ────────────────────────────────────────────────────────────

console.log(`\n${'─'.repeat(50)}`);
console.log(`Ran ${passed + failed} tests — ${passed} passed, ${failed} failed`);
console.log('─'.repeat(50));

if (failed > 0) process.exit(1);
