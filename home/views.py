from django.http import HttpResponse


def index(request):
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Search — TriangleIP</title>
<link rel='stylesheet' href='/static/tip_design.css'>
<style>
  .search-wrapper{position:relative;max-width:640px;}
  .search-input{width:100%;padding:12px 16px;border:1px solid var(--tip-border-color,#e5e7eb);border-radius:8px;font-size:15px;font-family:inherit;outline:none;transition:border-color .15s;}
  .search-input:focus{border-color:var(--tip-primary);}
  .suggest-dropdown{position:absolute;top:100%;left:0;right:0;background:#fff;border:1px solid var(--tip-border-color,#e5e7eb);border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.10);max-height:320px;overflow-y:auto;z-index:50;display:none;margin-top:4px;}
  .suggest-dropdown.open{display:block;}
  .suggest-item{padding:10px 16px;cursor:pointer;font-size:14px;border-bottom:1px solid #f3f4f6;display:flex;flex-direction:column;gap:2px;}
  .suggest-item:last-child{border-bottom:none;}
  .suggest-item:hover,.suggest-item.active{background:#f0f4ff;}
  .suggest-item .s-title{color:var(--tip-text,#111827);font-weight:500;}
  .suggest-item .s-sub{color:var(--tip-text-secondary,#6b7280);font-size:12px;}
  .source-select{padding:10px 14px;border:1px solid var(--tip-border-color,#e5e7eb);border-radius:8px;font-size:14px;font-family:inherit;outline:none;background:#fff;cursor:pointer;min-width:160px;}
  .source-select:focus{border-color:var(--tip-primary);}
  .placeholder-msg{text-align:center;padding:60px 20px;color:var(--tip-text-secondary,#6b7280);font-size:15px;}
  .loading-msg{text-align:center;padding:40px 20px;color:var(--tip-text-secondary,#6b7280);font-size:14px;}
  .loading-msg::before{content:'';display:inline-block;width:18px;height:18px;border:2px solid var(--tip-primary);border-top-color:transparent;border-radius:50%;animation:spin .6s linear infinite;margin-right:8px;vertical-align:middle;}
  @keyframes spin{to{transform:rotate(360deg);}}
  .detail-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;margin-top:20px;}
  .detail-card .label{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;color:var(--tip-text-secondary,#6b7280);margin-bottom:4px;}
  .detail-card .value{font-size:15px;color:var(--tip-text,#111827);font-weight:500;word-break:break-word;}
  .detail-card .value.empty{color:var(--tip-text-secondary,#6b7280);font-style:italic;}
  .diag-table{width:100%;border-collapse:collapse;font-size:13px;}
  .diag-table th,.diag-table td{padding:8px 12px;text-align:left;border-bottom:1px solid var(--tip-border-color,#e5e7eb);}
  .diag-table th{font-weight:600;color:var(--tip-text-secondary,#6b7280);width:160px;white-space:nowrap;}
  .diag-table td{color:var(--tip-text,#111827);word-break:break-all;}
  .diag-table code{background:#f3f4f6;padding:2px 6px;border-radius:4px;font-size:12px;}
  details summary{cursor:pointer;font-weight:600;font-size:14px;color:var(--tip-text,#111827);padding:12px 0;}
  details summary:hover{color:var(--tip-primary);}
</style>
</head>
<body>
<div class="tip-page">

  <h1 class="tip-page-title">Search</h1>
  <p style="color:var(--tip-text-secondary);margin-bottom:24px;font-size:14px;">Look up patents or attorneys using the TriangleIP database.</p>

  <!-- Source Selector -->
  <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:16px;">
    <label for="sourceSelect" style="font-size:14px;font-weight:600;color:var(--tip-text);">Source</label>
    <select id="sourceSelect" class="source-select">
      <option value="patent">Patent</option>
      <option value="attorney">Attorney</option>
    </select>
  </div>

  <!-- Search Box -->
  <div class="search-wrapper">
    <input id="searchInput" class="search-input" type="text" placeholder="Search patent…" autocomplete="off"/>
    <div id="suggestDropdown" class="suggest-dropdown"></div>
  </div>

  <!-- Results Area -->
  <div id="resultsArea" style="margin-top:28px;">
    <div class="placeholder-msg" id="placeholderMsg">
      <div style="font-size:32px;margin-bottom:12px;opacity:.35;">&#128269;</div>
      Select a source and start typing to search.
    </div>
  </div>

  <!-- Diagnostics -->
  <div class="tip-card" style="margin-top:40px;">
    <details>
      <summary>Diagnostics</summary>
      <div id="diagContent" style="margin-top:8px;">
        <p style="color:var(--tip-text-secondary);font-size:13px;">No API calls made yet.</p>
      </div>
    </details>
  </div>

</div>

<script>
const USER_REQUEST = "Build a page with a source selector and a dependent search. At the top, a dropdown to choose the search source \\u2014 Patent or Attorney. Below it, a search box whose behavior depends on the selected source. When the source changes, clear the current search and results, and update the placeholder. As I type (minimum 2 characters), call the suggest API for the selected source and show matching results in a dropdown. When I pick a result, call the details API and show the returned details in cards.";

const sourceSelect = document.getElementById('sourceSelect');
const searchInput = document.getElementById('searchInput');
const suggestDropdown = document.getElementById('suggestDropdown');
const resultsArea = document.getElementById('resultsArea');
const diagContent = document.getElementById('diagContent');

let suggestTimer = null;
let activeSuggestIndex = -1;
let currentSuggestItems = [];
let diagCalls = [];

/* ── Helpers ── */
function esc(s) {
  if (s === null || s === undefined) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function val(v, fallback) {
  if (v === null || v === undefined || v === '' || v === 'N/A' || v === '—') return fallback || '—';
  return v;
}

function showPlaceholder(msg) {
  resultsArea.innerHTML = '<div class="placeholder-msg"><div style="font-size:32px;margin-bottom:12px;opacity:.35;">&#128269;</div>' + esc(msg || 'Select a source and start typing to search.') + '</div>';
}

function showLoading() {
  resultsArea.innerHTML = '<div class="loading-msg">Loading details&hellip;</div>';
}

function showError(msg) {
  resultsArea.innerHTML = '<div class="tip-card" style="border-left:4px solid var(--tip-error,#ef4444);"><div style="font-weight:600;color:var(--tip-error,#ef4444);margin-bottom:4px;">Error</div><div style="font-size:14px;color:var(--tip-text-secondary);">' + esc(msg) + '</div></div>';
}

/* ── Diagnostics ── */
function recordCall(method, path, inputParams, outputFields, fieldMapping) {
  diagCalls.push({ method, path, inputParams, outputFields, fieldMapping });
  renderDiag();
}

function renderDiag() {
  if (!diagCalls.length) {
    diagContent.innerHTML = '<p style="color:var(--tip-text-secondary);font-size:13px;">No API calls made yet.</p>';
    return;
  }
  let h = '<div class="tip-table-wrap"><table class="diag-table"><thead><tr><th>#</th><th>Method</th><th>Endpoint</th><th>Input</th><th>Output Fields</th><th>Field Mapping</th></tr></thead><tbody>';
  diagCalls.forEach((c, i) => {
    h += '<tr><td>' + (i + 1) + '</td>';
    h += '<td>' + esc(c.method) + '</td>';
    h += '<td><code>' + esc(c.path) + '</code></td>';
    h += '<td><code>' + esc(JSON.stringify(c.inputParams)) + '</code></td>';
    h += '<td><code>' + esc(JSON.stringify(c.outputFields)) + '</code></td>';
    h += '<td style="font-size:12px;">' + esc(c.fieldMapping) + '</td></tr>';
  });
  h += '</tbody></table></div>';
  diagContent.innerHTML = h;
}

/* ── Source change ── */
sourceSelect.addEventListener('change', function() {
  searchInput.value = '';
  suggestDropdown.innerHTML = '';
  suggestDropdown.classList.remove('open');
  activeSuggestIndex = -1;
  currentSuggestItems = [];
  diagCalls = [];
  renderDiag();
  searchInput.placeholder = sourceSelect.value === 'patent' ? 'Search patent…' : 'Search attorney…';
  showPlaceholder();
  searchInput.focus();
});

/* ── Suggest ── */
searchInput.addEventListener('input', function() {
  const q = searchInput.value.trim();
  if (q.length < 2) {
    suggestDropdown.innerHTML = '';
    suggestDropdown.classList.remove('open');
    activeSuggestIndex = -1;
    currentSuggestItems = [];
    return;
  }
  clearTimeout(suggestTimer);
  suggestTimer = setTimeout(() => fetchSuggestions(q), 250);
});

searchInput.addEventListener('keydown', function(e) {
  if (!suggestDropdown.classList.contains('open')) return;
  const items = suggestDropdown.querySelectorAll('.suggest-item');
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    activeSuggestIndex = Math.min(activeSuggestIndex + 1, items.length - 1);
    updateActiveItem(items);
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    activeSuggestIndex = Math.max(activeSuggestIndex - 1, -1);
    updateActiveItem(items);
  } else if (e.key === 'Enter') {
    e.preventDefault();
    if (activeSuggestIndex >= 0 && currentSuggestItems[activeSuggestIndex]) {
      pickSuggestion(currentSuggestItems[activeSuggestIndex]);
    }
  } else if (e.key === 'Escape') {
    suggestDropdown.classList.remove('open');
    activeSuggestIndex = -1;
  }
});

function updateActiveItem(items) {
  items.forEach((el, i) => el.classList.toggle('active', i === activeSuggestIndex));
  if (activeSuggestIndex >= 0 && items[activeSuggestIndex]) {
    items[activeSuggestIndex].scrollIntoView({ block: 'nearest' });
  }
}

async function fetchSuggestions(q) {
  const source = sourceSelect.value;
  let url, params;
  if (source === 'patent') {
    url = '/tip-api/v1/patent-lookup/suggest';
    params = new URLSearchParams({ q: q, limit: '10' });
  } else {
    url = '/tip-api/v1/prosecutor/suggest';
    params = new URLSearchParams({ q: q, mode: 'att' });
  }
  try {
    const resp = await fetch(url + '?' + params.toString());
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const json = await resp.json();
    if (!json.status || !json.data || !Array.isArray(json.data)) {
      suggestDropdown.innerHTML = '';
      suggestDropdown.classList.remove('open');
      return;
    }
    currentSuggestItems = json.data;
    activeSuggestIndex = -1;
    renderSuggestions(json.data, source);
    recordCall('GET', url + '?' + params.toString(), { q: q, limit: 10, mode: source === 'attorney' ? 'att' : undefined }, ['data[].id', 'data[].text' + (source === 'patent' ? ', data[].display, data[].title, data[].type' : '')], 'data[] → suggestion dropdown items');
  } catch (err) {
    suggestDropdown.innerHTML = '';
    suggestDropdown.classList.remove('open');
  }
}

function renderSuggestions(items, source) {
  if (!items.length) {
    suggestDropdown.innerHTML = '<div style="padding:12px 16px;color:var(--tip-text-secondary);font-size:13px;">No results found</div>';
    suggestDropdown.classList.add('open');
    return;
  }
  let h = '';
  items.forEach((item, idx) => {
    if (source === 'patent') {
      const display = item.display || item.id || item.text || '';
      const title = item.title || '';
      h += '<div class="suggest-item" data-idx="' + idx + '">';
      h += '<span class="s-title">' + esc(display) + '</span>';
      if (title) h += '<span class="s-sub">' + esc(title) + '</span>';
      h += '</div>';
    } else {
      const text = item.text || item.id || '';
      h += '<div class="suggest-item" data-idx="' + idx + '">';
      h += '<span class="s-title">' + esc(text) + '</span>';
      h += '</div>';
    }
  });
  suggestDropdown.innerHTML = h;
  suggestDropdown.classList.add('open');
  suggestDropdown.querySelectorAll('.suggest-item').forEach(el => {
    el.addEventListener('click', function() {
      const idx = parseInt(this.getAttribute('data-idx'));
      if (currentSuggestItems[idx]) pickSuggestion(currentSuggestItems[idx]);
    });
  });
}

/* ── Pick suggestion & fetch details ── */
async function pickSuggestion(item) {
  suggestDropdown.classList.remove('open');
  activeSuggestIndex = -1;
  const source = sourceSelect.value;
  if (source === 'patent') {
    searchInput.value = item.display || item.id || item.text || '';
  } else {
    searchInput.value = item.text || item.id || '';
  }
  showLoading();
  try {
    if (source === 'patent') {
      await fetchPatentDetails(item.id || item.display || item.text);
    } else {
      await fetchAttorneyDetails(item.text || item.id);
    }
  } catch (err) {
    showError(err.message || 'Failed to load details.');
  }
}

/* ── Patent details ── */
async function fetchPatentDetails(query) {
  const url = '/tip-api/v1/patent-lookup/search';
  const body = { query: query };
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!resp.ok) {
    const errText = await resp.text().catch(() => '');
    throw new Error('HTTP ' + resp.status + (errText ? ': ' + errText : ''));
  }
  const json = await resp.json();
  if (!json.status) throw new Error(json.message || 'Search failed.');

  const summary = (json.data && json.data.result && json.data.result.summary) || {};
  const fields = {
    'Title': summary.title,
    'Application Number': summary.application_number,
    'Patent Number': summary.patent_number,
    'Status': summary.status,
    'Filing Date': summary.filing_date,
    'Grant Date': summary.grant_date,
    'Status Date': summary.status_date,
    'Application Type': summary.application_type,
    'Examiner': summary.examiner_name,
    'Group Art Unit': summary.group_art_unit,
    'Class / Subclass': summary.class_subclass,
    'Entity Status': summary.entity_status,
    'First Inventor': summary.first_inventor_name,
    'First Applicant': summary.first_applicant_name,
    'Earliest Publication': summary.earliest_publication_number,
    'Publication Date': summary.earliest_publication_date,
    'Docket Number': summary.docket_number,
    'Confirmation Number': summary.confirmation_number
  };

  const outputFields = {};
  Object.keys(fields).forEach(k => { outputFields['summary.' + k.toLowerCase().replace(/ /g, '_')] = fields[k]; });

  recordCall('POST', url, body, outputFields,
    'data.result.summary.* → detail cards');

  renderDetailCards('Patent Details', fields, summary.status);
}

/* ── Attorney details ── */
async function fetchAttorneyDetails(searchData) {
  const url = '/tip-api/v1/prosecutor/overview';
  const body = { search_data: searchData, mode: 'att' };
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!resp.ok) {
    const errText = await resp.text().catch(() => '');
    throw new Error('HTTP ' + resp.status + (errText ? ': ' + errText : ''));
  }
  const json = await resp.json();
  if (!json.status) throw new Error(json.message || 'Overview failed.');

  const ex = (json.data && json.data.ex_rule) || {};
  const profile = ex.profile || {};
  const oa = ex.oa || {};
  const pendency = ex.pendency || {};

  const fields = {
    'Name': profile.name,
    'Experience (Years)': profile.experience,
    'Group Art Units': profile.gau,
    'Total Applications': profile.total,
    'Granted': profile.granted,
    'Grant Rate': profile.grant_rate_text ? profile.grant_rate_text + '%' : null,
    'Application Range': profile.app_range,
    'Avg Office Actions': oa.average_oa,
    'Least Office Actions': oa.least_oa,
    'Most Office Actions': oa.most_oa,
    'Avg Pendency': pendency.average,
    'Shortest Pendency': pendency.shortest,
    'Longest Pendency': pendency.longest
  };

  const outputFields = {
    'profile.name': profile.name,
    'profile.experience': profile.experience,
    'profile.gau': profile.gau,
    'profile.total': profile.total,
    'profile.granted': profile.granted,
    'profile.grant_rate_text': profile.grant_rate_text,
    'profile.app_range': profile.app_range,
    'oa.average_oa': oa.average_oa,
    'oa.least_oa': oa.least_oa,
    'oa.most_oa': oa.most_oa,
    'pendency.average': pendency.average,
    'pendency.shortest': pendency.shortest,
    'pendency.longest': pendency.longest
  };

  recordCall('POST', url, body, outputFields,
    'data.ex_rule.profile/oa/pendency → detail cards');

  renderDetailCards('Attorney Profile', fields);
}

/* ── Render detail cards ── */
function renderDetailCards(sectionTitle, fields, statusField) {
  let statusTag = '';
  if (statusField) {
    const s = String(statusField).toLowerCase();
    let cls = 'tip-tag-default';
    if (s.includes('patent')) cls = 'tip-tag-success';
    else if (s.includes('pend')) cls = 'tip-tag-warning';
    else if (s.includes('aban') || s.includes('expir')) cls = 'tip-tag-error';
    statusTag = ' <span class="tip-tag ' + cls + '">' + esc(statusField) + '</span>';
  }

  let h = '<div class="tip-card" style="margin-bottom:20px;">';
  h += '<h2 style="font-size:18px;font-weight:600;color:var(--tip-text);margin-bottom:4px;">' + esc(sectionTitle) + statusTag + '</h2>';
  h += '</div>';

  h += '<div class="detail-grid">';
  Object.keys(fields).forEach(label => {
    const v = fields[label];
    const isEmpty = v === null || v === undefined || v === '';
    h += '<div class="tip-card detail-card">';
    h += '<div class="label">' + esc(label) + '</div>';
    h += '<div class="value' + (isEmpty ? ' empty' : '') + '">' + (isEmpty ? '—' : esc(v)) + '</div>';
    h += '</div>';
  });
  h += '</div>';

  resultsArea.innerHTML = h;
}

/* ── Close dropdown on outside click ── */
document.addEventListener('click', function(e) {
  if (!e.target.closest('.search-wrapper')) {
    suggestDropdown.classList.remove('open');
    activeSuggestIndex = -1;
  }
});
</script>
</body>
</html>"""
    return HttpResponse(html, content_type="text/html")
