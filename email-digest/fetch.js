#!/usr/bin/env node
// Fetches Gmail messages labeled "direct" from the last 24 hours via the `gws`
// CLI, decodes bodies, strips quoted replies/signatures, and prints a JSON
// array to stdout. No action-item extraction — that is the caller's job.

const { execFileSync } = require('node:child_process');

function runGws(args, paramsObj) {
  const fullArgs = [...args, '--params', JSON.stringify(paramsObj)];
  const out = execFileSync('gws', fullArgs, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'inherit'] });
  return JSON.parse(out);
}

function getHeader(headers, name) {
  const h = (headers || []).find(x => (x.name || '').toLowerCase() === name.toLowerCase());
  return h?.value || '';
}

function base64UrlDecodeToUtf8(s) {
  if (!s) return '';
  const b64 = s.replace(/-/g, '+').replace(/_/g, '/');
  const pad = '='.repeat((4 - (b64.length % 4)) % 4);
  return Buffer.from(b64 + pad, 'base64').toString('utf8');
}

function htmlToText(html) {
  return (html || '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/p>/gi, '\n\n')
    .replace(/<\/(div|li|tr|h[1-6])>/gi, '\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function collectParts(payload, plain = [], html = []) {
  if (!payload) return { plain, html };
  if (payload.mimeType === 'text/plain' && payload.body?.data) {
    plain.push(base64UrlDecodeToUtf8(payload.body.data));
  } else if (payload.mimeType === 'text/html' && payload.body?.data) {
    html.push(base64UrlDecodeToUtf8(payload.body.data));
  }
  if (payload.parts?.length) {
    for (const p of payload.parts) collectParts(p, plain, html);
  }
  return { plain, html };
}

function stripQuotedAndFooters(text) {
  let t = text || '';
  t = t.split(/\nOn .*wrote:\n/i)[0];
  t = t.split(/\n[-]{2,}\s*Forwarded message\s*[-]{2,}\n/i)[0];
  t = t.split(/\n--\s*\n/)[0];
  t = t.replace(/\r\n/g, '\n').trim();
  return t;
}

function main() {
  let list;
  try {
    list = runGws(['gmail', 'users', 'messages', 'list'], {
      userId: 'me',
      q: 'label:direct newer_than:1d',
      maxResults: 100,
    });
  } catch (e) {
    process.stderr.write(`gws list failed: ${e.message}\n`);
    process.exit(2);
  }

  const messages = list.messages || [];
  const results = [];

  for (const m of messages) {
    let msg;
    try {
      msg = runGws(['gmail', 'users', 'messages', 'get'], {
        userId: 'me',
        id: m.id,
        format: 'full',
      });
    } catch (e) {
      process.stderr.write(`gws get failed for ${m.id}: ${e.message}\n`);
      continue;
    }

    const headers = msg.payload?.headers || [];
    const subject = getHeader(headers, 'Subject') || '(no subject)';
    const from = getHeader(headers, 'From') || '(unknown sender)';
    const date = getHeader(headers, 'Date') || '';

    const { plain, html } = collectParts(msg.payload);
    let body = plain.join('\n\n');
    if (!body && html.length) body = htmlToText(html.join('\n\n'));
    body = stripQuotedAndFooters(body) || (msg.snippet || '');

    results.push({
      id: msg.id,
      threadId: msg.threadId,
      subject,
      from,
      date,
      bodyText: body,
      snippet: msg.snippet || '',
    });
  }

  process.stdout.write(JSON.stringify(results, null, 2) + '\n');
}

main();
