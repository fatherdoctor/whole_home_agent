#!/usr/bin/env python3
"""Check current Markdown/prose labels without changing documents or contacting services."""
import argparse
import fnmatch
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
CODE_LANGUAGES = {'python', 'py', 'json', 'yaml', 'yml', 'toml', 'ini', 'bash', 'sh',
                  'shell', 'javascript', 'js', 'html', 'css', 'mermaid'}
SKIP_DIRS = {'.git', '.storage', '.claude', 'node_modules', '__pycache__'}


# Reviewed transition ceiling from f480765fd16b, separate from the editable data.
# Data entries may shrink freely. Expanding this ceiling is an explicit code-policy
# change: the PR must name the affected wording and explain why it needs an exception.
REVIEWED_BASELINE_LIMITS = {
    ('00-start-here/README.md', 'apps', 'c3d6aa1d6201360e1a9d92090147933634ae82ffcc0cf73d8d1d8af5bfb5954f'): 1,
    ('00-start-here/chat-app-starter.md', 'apps', '6928ba1e26372e38a7943b198ab046e400294167169f7db58a4bfc0652a3bb93'): 1,
    ('00-start-here/chat-app-starter.md', 'marketplace', '11bafbd3469115541f06f9bc838efaad0fe498430f3b21f78f3be65b7b166f99'): 1,
    ('00-start-here/chat-app-starter.md', 'marketplace', '61174a9a950fccc261a881bdc3d47681ba208e213895212c869f6701ab25a016'): 1,
    ('00-start-here/chat-app-starter.md', 'marketplace', '6928ba1e26372e38a7943b198ab046e400294167169f7db58a4bfc0652a3bb93'): 2,
    ('00-start-here/from-a-chat-app.md', 'apps', '6928ba1e26372e38a7943b198ab046e400294167169f7db58a4bfc0652a3bb93'): 1,
    ('00-start-here/from-a-chat-app.md', 'marketplace', '11bafbd3469115541f06f9bc838efaad0fe498430f3b21f78f3be65b7b166f99'): 1,
    ('00-start-here/from-a-chat-app.md', 'marketplace', '6928ba1e26372e38a7943b198ab046e400294167169f7db58a4bfc0652a3bb93'): 2,
    ('AGENTS.md', 'apps', '1c6e782f4913d94e96f96cf916f08227ae8e1cefad6864856cd64ab0311baaf5'): 1,
    ('AGENTS.md', 'marketplace', '549dc4f3f3e24ef429978588d402c9a0ab5770f091e2b0699b9465894e6d02cc'): 1,
    ('CHANGELOG.md', 'apps', '2ffeac95ad882d2b2d50b29e7377a610d7cf9313e70ea73b21501908853ebaf8'): 1,
    ('adapters/agents/claude-code.md', 'apps', '93b70f128e65415c518c2eca05f9a7b825740dbbda3c43110878c95b63cec7ae'): 2,
    ('adapters/agents/claude-code.md', 'apps', 'bfee0ca8b6587ba0a4caa2f5e9a625e050d06073503fb992d7b85e9673cebcfe'): 2,
    ('docs/readme-style.md', 'marketplace', '3ee55bfb55c8b58354f718f5a04b045314574246b13e0b83ec15ad4cdecc209e'): 1,
    ('docs/readme-style.md', 'marketplace', '7df9c446ff9198d70c2592ce6c8c34d10b851812dc70b79a12c9a9800fd5d05a'): 1,
    ('docs/readme-style.md', 'marketplace', '8b8dc21f6dbd55954656c2784fe01f682e02bad7d82985de6e5ea79c377e2b8a'): 1,
    ('examples/pi-matter-apple.md', 'tools', '6a2a53f1357a52308057d855bd2cfd1302d09af21ce7eeb503c0ebd85ff514e3'): 1,
    ('examples/pi-matter-apple.md', 'tools', 'e7198d3e141f0b2eacda81abf846c934116fb5f4f1eb2ccd35bc4fdfa5ddb1fc'): 1,
    ('install/agent-access.md', 'apps', '0ab4f49a1dca5e6d18b979b83cbaa88dd60800165361946064535df6449ff084'): 2,
    ('install/network-and-backups-first.md', 'marketplace', '61174a9a950fccc261a881bdc3d47681ba208e213895212c869f6701ab25a016'): 1,
    ('templates/docs/board.md', 'tools', 'fafa6cf62c2a43f7e3becdc80cba703658339e82da871da7ab0fb0a2c7d1db03'): 1,
}


def baseline_identity(row):
    return row['path'], row['rule'], row['sha256']


def baseline_growth(rows):
    """Report additions, replacements and count increases beyond the reviewed ceiling."""
    return [dict(row, allowed_count=REVIEWED_BASELINE_LIMITS.get(baseline_identity(row), 0))
            for row in rows if row['count'] > REVIEWED_BASELINE_LIMITS.get(baseline_identity(row), 0)]


def load_data(path):
    data = json.loads(path.read_text(encoding='utf-8'))
    if (not isinstance(data, dict) or data.get('schema_version') != 1
            or not isinstance(data.get('terms'), list) or not data['terms']):
        raise ValueError('Unsupported or empty terminology data')
    seen = set()
    for term in data['terms']:
        if (not isinstance(term, dict) or not all(isinstance(term.get(k), str) and term[k] for k in ('id', 'current', 'release', 'source'))
                or not re.fullmatch(r'\d{4}\.\d{1,2}', term['release'])
                or not term['source'].startswith('https://www.home-assistant.io/')
                or not isinstance(term.get('old'), list) or not term['old']
                or any(not isinstance(s, str) or not s for s in term['old'])
                or term['id'] in seen):
            raise ValueError('Invalid terminology record')
        seen.add(term['id'])
    if (not isinstance(data.get('code_identifiers', []), list)
            or any(not isinstance(s, str) for s in data.get('code_identifiers', []))
            or not isinstance(data.get('allowlist', []), list)):
        raise ValueError('Invalid exceptions')
    for entry in data.get('allowlist', []):
        if not isinstance(entry, dict) or not entry.get('path') or not entry.get('reason'):
            raise ValueError('Every exception needs a path and reason')
        if entry.get('scope') == 'file':
            if any(c in entry['path'] for c in '*?[') or not re.search(r'\d{4}-\d{2}-\d{2}', entry['path']):
                raise ValueError('Whole-file exceptions require an exact dated historical path')
        elif (not entry.get('text') or any(c in entry['path'] for c in '*?[')):
            raise ValueError('A prose exception needs exact text and an exact path')
    return data


def mask_span(match):
    # A barrier, rather than spaces, prevents matching a phrase across ignored content.
    return '\x01' * len(match.group())


def visible_text(text, identifiers):
    """Return paragraph text and offsets into its source, retaining true code identifiers."""
    chars = list(text)
    for identifier in identifiers:
        if '-' not in identifier:
            continue  # Bare words can still be visible labels; only named hyphenated identifiers qualify.
        for match in re.finditer(r'(?<![\w-])' + re.escape(identifier) + r'(?![\w-])', text):
            chars[match.start():match.end()] = '\x01' * len(match.group())
    removed, protected = set(), set()
    for match in re.finditer(r'(`+)([^`]*?)\1', text):
        value = match.group(2)
        if value in identifiers or re.fullmatch(r'[a-z0-9]+(?:[/_.-][a-z0-9_-]+)+', value):
            chars[match.start():match.end()] = '\x01' * len(match.group())
        else:
            removed.update(range(match.start(), match.start(2)))
            removed.update(range(match.end(2), match.end()))
            protected.update(range(match.start(2), match.end(2)))
    for match in re.finditer(r'https?://[^\s<>)]*', text):
        chars[match.start():match.end()] = '\x01' * len(match.group())
    for match in re.finditer(r'\{\{[^{}]*\}\}', text):
        chars[match.start():match.end()] = '\x01' * len(match.group())
    for match in re.finditer(r'\\([!"#$%&\'()*+,\-./:;<=>?@\[\]^_`{|}~])', text):
        removed.add(match.start())
    # Underscores inside words are identifiers, not Markdown emphasis. Asterisks may be intraword.
    for pattern in (r'(\*{1,3})(?=\S)(.+?)(?<=\S)\1',
                    r'(?<!\w)(_{1,3})(?=\S)(.+?)(?<=\S)\1(?!\w)'):
        for match in re.finditer(pattern, ''.join(chars)):
            delimiters = list(range(match.start(), match.start(2))) + list(range(match.end(2), match.end()))
            if not any(index in protected for index in delimiters):
                removed.update(delimiters)
    offsets = [index for index in range(len(chars)) if index not in removed]
    return ''.join(chars[index] for index in offsets), offsets


def markdown_content(line):
    """Peel list/quote containers while retaining the indentation relevant to a fenced block."""
    quote_depth, indent, item = 0, 0, False
    while True:
        quote = re.match(r'^[ \t]*>[ \t]?', line)
        if quote:
            quote_depth += 1
            line = line[quote.end():]
            indent = 0
            continue
        bullet = re.match(r'^[ \t]*(?:[-+*]|[0-9]+[.)])[ \t]+', line)
        if bullet:
            indent += bullet.end()
            line = line[bullet.end():]
            item = True
            continue
        break
    indent += len(line) - len(line.lstrip(' \t'))
    return line.lstrip(' \t'), quote_depth, indent, item


def check_text(text, path, data):
    exceptions = [e for e in data.get('allowlist', []) if fnmatch.fnmatchcase(path, e['path'])]
    if any(e.get('scope') == 'file' for e in exceptions):
        return []
    patterns = [(term, re.compile(r'(?<!\w)(?:' + '|'.join(
        r'\s+'.join(re.escape(word) for word in phrase.split())
        for phrase in sorted(term['old'], key=len, reverse=True)) + r')(?!\w)', re.I))
        for term in data['terms']]
    findings, seen, paragraph = [], set(), []

    def flush():
        if not paragraph:
            return
        joined = ' '.join(line for _, line in paragraph)
        source_lines = []
        for number, line in paragraph:
            source_lines.extend([number] * (len(line) + 1))
        visible, offsets = visible_text(joined, set(data.get('code_identifiers', [])))
        for entry in exceptions:
            if entry.get('text'):
                visible = re.sub(re.escape(entry['text']), mask_span, visible)
        for term, pattern in patterns:
            for match in pattern.finditer(visible):
                number = source_lines[offsets[match.start()]]
                key = (number, term['id'])
                if key not in seen:
                    seen.add(key)
                    findings.append({'path': path, 'line': number, 'rule': term['id'],
                                     'current': term['current'], 'release': term['release'],
                                     'sha256': hashlib.sha256(joined.encode()).hexdigest()})
        paragraph.clear()

    # Preserve source lines without exposing comment text as visible prose.
    text = re.sub(r'<!--[\s\S]*?(?:-->|\Z)',
                  lambda match: ''.join('\n' if ch == '\n' else '\x01' for ch in match.group()), text)
    fence, code, previous_quote = None, False, None
    list_indent = 0
    for number, raw in enumerate(text.splitlines(), 1):
        line, quote, indent, item = markdown_content(raw)
        if item:
            list_indent = indent
        elif line and indent < list_indent:
            list_indent = 0
        if fence and line and (quote < fence[1] or (quote == fence[1] and indent < fence[2])):
            flush()
            fence, code = None, False  # Leaving a container implicitly ends its fenced block.
        marker = re.fullmatch(r'(`{3,}|~{3,})(.*)', line)
        if marker:
            marks, info = marker.groups()
            if fence is None:
                flush()
                fence = (marks, quote, indent)
                language = info.strip().split()[0].lower() if info.strip() else ''
                code = language in CODE_LANGUAGES
                continue
            if marks[0] == fence[0][0] and len(marks) >= len(fence[0]) and not info.strip():
                flush()
                fence, code = None, False
                continue
        if code:
            continue
        if fence is None and ((indent >= list_indent + 4 and not paragraph and not item)
                              or re.match(r'^\[[^\]]+\]:\s*\S', line)):
            flush()
            continue
        if not line:
            flush()
            continue
        block_line = bool(re.match(r'(?:#{1,6}\s|\|)', line))
        if item or block_line or quote != previous_quote:
            flush()
        paragraph.append((number, line.strip()))
        previous_quote = quote
        if block_line:
            flush()
    flush()
    order = {term['id']: index for index, term in enumerate(data['terms'])}
    return sorted(findings, key=lambda row: (row['line'], order[row['rule']]))


def check_root(root, data):
    findings, files = [], 0
    def unreadable_directory(error):
        raise error
    for parent, dirs, names in os.walk(root, followlinks=False, onerror=unreadable_directory):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not (Path(parent) / d).is_symlink())
        for name in sorted(names):
            path = Path(parent) / name
            if (path.is_symlink() or path.suffix.lower() not in ('.md', '.rst', '.txt')
                    or re.fullmatch(r'(?:secrets?|tokens?|passwords?|credentials?|pin)\.(?:txt|rst)', name, re.I)):
                continue
            files += 1
            findings.extend(check_text(path.read_text(encoding='utf-8'), path.relative_to(root).as_posix(), data))
    return {'files': files, 'count': len(findings), 'findings': findings}


def baseline_counts(findings):
    """Count exact file/rule/paragraph identities; line shifts do not renew an exception."""
    return Counter((row['path'], row['rule'], row['sha256']) for row in findings)


def new_findings(findings, baseline):
    remaining = Counter(baseline)
    added = []
    for row in findings:
        key = (row['path'], row['rule'], row['sha256'])
        if remaining[key] > 0:
            remaining[key] -= 1
        else:
            added.append(row)
    return added


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=HERE.parents[1])
    parser.add_argument('--data', type=Path, default=HERE / 'ha-terms.json')
    parser.add_argument('--report-only', action='store_true', help='Report findings with exit 0; data/read errors still fail')
    parser.add_argument('--json', action='store_true', help='Emit locations and rule IDs, never source lines')
    parser.add_argument('--ratchet', action='store_true', help='Fail on findings outside the committed baseline')
    args = parser.parse_args(argv)
    try:
        if not args.root.is_dir():
            raise ValueError('Document root is not a directory')
        data = load_data(args.data)
        result = check_root(args.root, data)
        if args.ratchet:
            baseline = {}
            for row in data['baseline']:
                if (set(row) != {'path', 'rule', 'sha256', 'count'}
                        or not isinstance(row['path'], str) or not isinstance(row['rule'], str)
                        or not re.fullmatch(r'[0-9a-f]{64}', row['sha256'])
                        or type(row['count']) is not int or row['count'] <= 0):
                    raise ValueError('Invalid baseline record')
                key = (row['path'], row['rule'], row['sha256'])
                if key in baseline:
                    raise ValueError('Duplicate baseline record')
                baseline[key] = row['count']
            result['baseline_growth'] = baseline_growth(data['baseline'])
            result['new_findings'] = new_findings(result['findings'], baseline)
            result['new_count'] = len(result['new_findings'])
    except (OSError, UnicodeError, ValueError, TypeError, KeyError):
        print('Terminology check could not read valid data or documents.', file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        for item in result['findings']:
            print(f"{item['path']}:{item['line']}: {item['rule']}: use {item['current']} (since {item['release']})")
        print(f"HA terms: {result['count']} findings in {result['files']} files; "
              + ('report-only' if args.report_only else 'enforcing'))
    if args.ratchet:
        if result['baseline_growth'] and not args.json:
            print('Baseline growth requires separate review and an explanation in the PR; the data may only shrink.')
            for row in result['baseline_growth']:
                print(f"{row['path']}: {row['rule']}: baseline count {row['count']} exceeds reviewed {row['allowed_count']}")
        return 1 if result['new_count'] or result['baseline_growth'] else 0
    return 0 if args.report_only or not result['count'] else 1


if __name__ == '__main__':
    sys.exit(main())
