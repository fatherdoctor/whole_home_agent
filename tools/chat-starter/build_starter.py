#!/usr/bin/env python3
"""build_starter.py - build the one-file starter for a chat app that cannot open web addresses.

Run from the kit's root:  python3 tools/chat-starter/build_starter.py           (writes the file)
                          python3 tools/chat-starter/build_starter.py --check   (exit 1 if it is out of date)

Status: written (KIT-CHAT0, 2026-11-10). Standard library only.

The output, 00-start-here/chat-app-starter.md, is 00-start-here/from-a-chat-app.md followed by the pages and
sections it names, each under a "Part" heading with its kit path, so a chat app given this one attachment has the
whole first evening. Rebuild after editing any source in SOURCES; --check (and the test beside this file) says
when the committed copy is stale. The same sources always build the same file.
Literal Markdown examples must use fences; indented examples are treated as prose.
"""
import argparse
import pathlib
import posixpath
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = "00-start-here/chat-app-starter.md"

# (kit path, section heading or None for the whole file), in reading order.
SOURCES = [
    ("00-start-here/from-a-chat-app.md", None),
    ("adapters/agents/chat-apps.md", None),
    ("interview/phase-0-setup-interview.md", None),
    ("install/ha-green.md", None),
    ("install/raspberry-pi.md", None),
    ("install/mini-pc-bare-metal.md", None),
    ("install/proxmox-vm.md", None),
    ("install/network-and-backups-first.md", None),
    ("install/voice-assistants.md", None),
    ("00-start-here/your-first-automation.md", None),
    ("adapters/agents/claude-code.md", "Install on the box and sign in"),
    ("adapters/agents/codex.md", "Install on the box and sign in"),
]

HEADER = """# Whole Home Agent - the starter file for a chat app

*Built by `tools/chat-starter/build_starter.py` from {count} kit sources; do not edit by hand, edit the sources and
rebuild. For a chat app that cannot open web addresses: attach this one file and say
"Follow this file." Start with Part 1. A path such as `install/ha-green.md` names a Part below when it is
included; anything else lives in the full kit, which the agent on the box reads after the hand-off.*

Parts: {toc}
"""


FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*$")
REFERENCE_TARGET = re.compile(
    r"^((?: {0,3}>[ \t]?| {0,3}(?:[-+*]|[0-9]{1,9}[.)])[ \t]+)*"
    r" {0,3}\[[^]\n]+\]:[ \t]*)(<[^>]+>|[^\s]+)")
REFERENCE_LABEL = re.compile(r"^ {0,3}\[[^]\n]+\]:[ \t]*$")
REFERENCE_CONTINUATION = re.compile(r"^( {0,3})(<[^>]+>|[^\s]+)")
LINK_TARGET = re.compile(r"(\]\()(<[^>]+>|[^()\s]+)(?=(?:\s+[^)]*)?\))")


def strip_containers(line, containers):
    """Remove only the list/quote prefixes belonging to an existing container."""
    kept = []
    for container in containers:
        kind, width, _ = container
        if not line.strip():
            # A blank line alone does not end a list; the next content decides.
            return line, list(containers)
        if kind == 'quote':
            prefix = re.match(r'^ {0,3}>[ \t]?', line)
            if not prefix:
                break
            line = line[prefix.end():]
        else:
            if not line.startswith(' ' * width):
                break
            line = line[width:]
        kept.append(container)
    return line, kept


def container_lines(text):
    """Classify fences with content offsets and stable list-item/quote identities."""
    fence, containers = None, []
    next_identity = 0
    for original in text.splitlines():
        content, kept = strip_containers(original, containers)
        if fence and (len(kept) == len(containers) or not original.strip()):
            yield original, True, len(original) - len(content), tuple(c[2] for c in containers)
            char, size = fence
            if re.fullmatch(r' {0,3}' + re.escape(char) + '{' + str(size) + r',}[ \t]*', content):
                fence = None
            continue
        # Leaving an unclosed list or quote fence ends that container's code.
        fence, containers = None, kept
        while True:
            quote = re.match(r'^ {0,3}>[ \t]?', content)
            item = re.match(r'^( {0,3})([-+*]|[0-9]{1,9}[.)])(?:( {1,4})(\S.*)?|[ \t]*)$', content)
            if quote:
                next_identity += 1
                containers.append(('quote', 0, next_identity))
                content = content[quote.end():]
            elif item:
                spacing = len(item.group(3)) if item.group(3) else 1
                width = len(item.group(1)) + len(item.group(2)) + spacing
                next_identity += 1
                containers.append(('list', width, next_identity))
                content = item.group(4) or ''
            else:
                break
        opening = FENCE_OPEN.match(content)
        if opening and not (opening.group(1)[0] == '`' and '`' in opening.group(2)):
            fence = opening.group(1)[0], len(opening.group(1))
        yield original, fence is not None, len(original) - len(content), tuple(c[2] for c in containers)


def fenced_lines(text):
    """Keep a fence in its opening container; extra quote markers inside are code."""
    for line, fenced, _, _ in container_lines(text):
        yield line, fenced


def section_bounds(lines, heading):
    """Locate the named section in already classified lines."""
    start = None
    for i, (line, in_fence) in enumerate(lines):
        if not in_fence and re.fullmatch(r"##\s+" + re.escape(heading) + r"\s*", line):
            start = i
            break
    if start is None:
        raise SystemExit(f"build_starter: section '## {heading}' not found")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        line, in_fence = lines[j]
        if not in_fence and re.match(r"#{1,2}\s", line):
            end = j
            break
    return start, end


def section(text, heading):
    """The named level-two section, ignoring heading-like lines inside code fences."""
    lines = list(fenced_lines(text))
    start, end = section_bounds(lines, heading)
    return "\n".join(line for line, _ in lines[start:end]).strip() + "\n"


def demote(text):
    """Push headings down two levels while preserving all fenced code."""
    return "\n".join("##" + line if not fenced and re.match(r"#{1,4}\s", line) else line
                     for line, fenced in fenced_lines(text)).strip() + "\n"


def heading_slug(title):
    """Approximate Markdown heading fragments, including duplicate numbering per source."""
    title = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", title)
    title = re.sub(r"<[^>]+>", "", title)
    title = re.sub(r"[ \t]+#+[ \t]*$", "", title).lower()
    title = re.sub(r"[^\w -]", "", title)
    return title.strip().replace(" ", "-")


def next_fragment(slug, used):
    """Disambiguate repeated headings, including collisions with numbered titles."""
    fragment, number = slug, 0
    while fragment in used:
        number += 1
        fragment = f"{slug}-{number}"
    used.add(fragment)
    return fragment


def heading_anchors(body, number, *, source=None, section_heading=None):
    """Map included headings using fragment numbering from their full source file."""
    used, anchors = set(), {}
    lines = list(fenced_lines(source if section_heading else body))
    start, end = section_bounds(lines, section_heading) if section_heading else (0, len(lines))
    for index, (line, fenced) in enumerate(lines):
        match = HEADING.match(line) if not fenced else None
        if not match:
            continue
        fragment = next_fragment(heading_slug(match.group(2)), used)
        if start <= index < end:
            anchors[fragment] = f"starter-part-{number}--{fragment}"
    return anchors


def rewrite_links(line, source_path, targets, *, content_offset=0, reference_continuation=False):
    """Rewrite links and reference destinations relative to their active container."""
    def replace(match):
        raw = match.group(2)
        target = raw[1:-1] if raw.startswith('<') and raw.endswith('>') else raw
        try:
            parsed = urlsplit(target)
        except ValueError:
            return match.group(0)
        if parsed.scheme or parsed.netloc or parsed.query or parsed.path.startswith('/'):
            return match.group(0)
        path = (posixpath.normpath(posixpath.join(posixpath.dirname(source_path), unquote(parsed.path)))
                if parsed.path else source_path)
        info = targets.get(path)
        if info is None:
            return match.group(0)
        number, anchors, whole_file = info[:3]
        if parsed.fragment:
            destination = anchors.get(unquote(parsed.fragment))
            if destination is None:
                # Existing headings outside a selected section still belong to
                # the full kit. A typo or removed heading is never such a link.
                full_anchors = info[3] if len(info) > 3 else anchors
                if whole_file or unquote(parsed.fragment) not in full_anchors:
                    raise SystemExit(f'build_starter: unresolved link in {source_path}: {target}')
                return match.group(0)  # The requested section is not included.
        else:
            if not whole_file:
                return match.group(0)  # A single section is not the complete target file.
            destination = f"starter-part-{number}"
        return match.group(1) + '#' + destination

    # Definitions carry the destination for full, collapsed and shortcut links.
    # Keep container prefixes separate so continued list indentation stays intact.
    # Process them before splitting code spans: a title may contain backticks.
    reference = REFERENCE_CONTINUATION if reference_continuation else REFERENCE_TARGET
    definition = reference.match(line[content_offset:])
    if definition:
        return line[:content_offset] + replace(definition) + line[content_offset + definition.end():]
    pieces = re.split(r"(`+)", line)
    code = None
    for i, piece in enumerate(pieces):
        if piece and set(piece) == {'`'}:
            if code is None:
                code = len(piece)
            elif len(piece) == code:
                code = None
        elif code is None:
            pieces[i] = LINK_TARGET.sub(replace, piece)
    return ''.join(pieces)


def render_part(body, source_path, anchors, targets):
    out, anchor_ids = [], iter(anchors.values())
    # Equal indentation can belong to a new item or quote. Continue a reference
    # only while its original container identities survive on the next line.
    pending_reference = None
    for line, fenced, content_offset, container_id in container_lines(body):
        match = HEADING.match(line) if not fenced else None
        if match:
            out.append(f'<a id="{next(anchor_ids)}"></a>')
        if not fenced:
            content = line[content_offset:]
            line = rewrite_links(line, source_path, targets, content_offset=content_offset,
                                 reference_continuation=pending_reference == container_id)
            pending_reference = container_id if REFERENCE_LABEL.fullmatch(content) else None
            if re.match(r"#{1,4}\s", line):
                line = "##" + line
        else:
            pending_reference = None
        out.append(line)
    return "\n".join(out).strip() + "\n"


def build(root=ROOT):
    parts, full_anchors = [], {}
    for number, (path, heading) in enumerate(SOURCES, 1):
        src = (root / path).read_text(encoding="utf-8")
        body = section(src, heading) if heading else src
        anchors = heading_anchors(body, number, source=src, section_heading=heading)
        full_anchors[path] = heading_anchors(src, number)
        parts.append((path, heading, body, anchors))
    targets = {path: (n, anchors, heading is None, full_anchors[path])
               for n, (path, heading, _, anchors) in enumerate(parts, 1)}
    toc = "; ".join(f"{n} `{p}`" + (f" ({h})" if h else "")
                    for n, (p, h, _, _) in enumerate(parts, 1))
    out = [HEADER.format(count=len(parts), toc=toc)]
    for n, (path, heading, body, anchors) in enumerate(parts, 1):
        title = f"`{path}`" + (f", section \"{heading}\"" if heading else "")
        out.append(f'\n---\n\n<a id="starter-part-{n}"></a>\n## Part {n}: {title}\n\n'
                   + render_part(body, path, anchors, targets))
    return "".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the committed file is out of date")
    args = ap.parse_args(argv)
    text = build()
    target = ROOT / OUT
    if args.check:
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        if current != text:
            print(f"{OUT} is out of date: run python3 tools/chat-starter/build_starter.py")
            return 1
        print(f"{OUT} is current ({len(text)} characters, {len(text.encode('utf-8'))} bytes)")
        return 0
    target.write_text(text, encoding="utf-8")
    print(f"wrote {OUT} ({len(text)} characters, {len(text.encode('utf-8'))} bytes, {len(SOURCES)} parts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
