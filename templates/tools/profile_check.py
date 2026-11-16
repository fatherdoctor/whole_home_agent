#!/usr/bin/env python3
"""Read the kit profile's YAML subset and check its shape, using only the standard library.

No profile values are printed and nothing is rewritten. A shape pass is not a readiness pass.
Unsupported YAML (tags, anchors, block strings, multiple documents) is unverified, never silently accepted.
"""
import argparse
import datetime
import json
import math
import pathlib
import re
import sys


class ProfileError(ValueError):
    def __init__(self, reason, line=None, unsupported=False):
        self.reason, self.line, self.unsupported = reason, line, unsupported
        super().__init__(reason)


def split_flow(text, separator=","):
    parts, start, stack, quote, escaped = [], 0, [], None, False
    i = 0
    while i < len(text):
        ch = text[i]
        if quote:
            if quote == '"' and escaped:
                escaped = False
            elif quote == '"' and ch == "\\":
                escaped = True
            elif ch == quote:
                if quote == "'" and i + 1 < len(text) and text[i + 1] == "'":
                    i += 1
                else:
                    quote = None
        elif ch in "'\"" and (i == 0 or text[i - 1] in " [{,:"):
            quote = ch
        elif ch in "[{":
            stack.append(ch)
        elif ch in "]}":
            if not stack or (stack.pop(), ch) not in (("[", "]"), ("{", "}")):
                raise ProfileError("unbalanced_flow")
        elif ch == separator and not stack:
            if separator != ":" or i + 1 == len(text) or text[i + 1].isspace():
                parts.append(text[start:i].strip())
                start = i + 1
                if separator == ":":
                    return parts + [text[start:].strip()]
        i += 1
    if quote or stack:
        raise ProfileError("unterminated_quote_or_flow", unsupported=True)
    parts.append(text[start:].strip())
    return parts


def scalar(text, depth=0):
    if depth > 32:
        raise ProfileError("nesting_limit", unsupported=True)
    text = text.strip()
    if not text:
        return None
    if text.startswith(("&", "*", "!", "|", ">")):
        raise ProfileError("unsupported_yaml_construct", unsupported=True)
    if text[0] in "'\"":
        if text[-1] != text[0] or len(text) < 2:
            raise ProfileError("unterminated_quote", unsupported=True)
        try:
            if text[0] == '"':
                return json.loads(text)
            inner, i = text[1:-1], 0
            while i < len(inner):
                if inner[i] == "'":
                    if i + 1 >= len(inner) or inner[i + 1] != "'":
                        raise ValueError
                    i += 1
                i += 1
            return inner.replace("''", "'")
        except ValueError:
            raise ProfileError("unsupported_quoted_scalar", unsupported=True) from None
    if text[0] in "[{":
        closing = "]" if text[0] == "[" else "}"
        if not text.endswith(closing):
            raise ProfileError("unbalanced_flow")
        inner = text[1:-1].strip()
        parts = split_flow(inner) if inner else []
        if parts and parts[-1] == "":
            parts.pop()
        if any(not item for item in parts):
            raise ProfileError("empty_flow_item")
        if text[0] == "[":
            return [scalar(item, depth + 1) for item in parts]
        out = {}
        for item in parts:
            key, value = pair(item)
            if key in out:
                raise ProfileError("duplicate_key")
            out[key] = scalar(value, depth + 1)
        return out
    low = text.lower()
    if low in ("null", "~"):
        return None
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if re.fullmatch(r"-?\d+\.\d+(?:[eE][+-]?\d+)?", text):
        value = float(text)
        if not math.isfinite(value):
            raise ProfileError("nonfinite_number")
        return value
    if low in (".nan", ".inf", "-.inf", "+.inf") or re.search(r":\s", text):
        raise ProfileError("unsupported_scalar", unsupported=True)
    if text.startswith(("]", "}", "---", "...")):
        raise ProfileError("unsupported_scalar", unsupported=True)
    return text


def pair(text):
    parts = split_flow(text, ":")
    if len(parts) != 2 or not parts[0]:
        raise ProfileError("expected_mapping")
    # Profile keys are text: in particular the documented adoption key "on" is not a boolean.
    key_text = parts[0]
    if key_text.startswith(("&", "*", "!", "|", ">", "[", "{")):
        raise ProfileError("unsupported_mapping_key", unsupported=True)
    key = scalar(key_text) if key_text.startswith(("'", '"')) else key_text
    if not isinstance(key, str):
        raise ProfileError("mapping_key_must_be_text")
    return key, parts[1]


def strip_comment(text):
    quote, escaped, i = None, False, 0
    while i < len(text):
        ch = text[i]
        if quote:
            if quote == '"' and escaped:
                escaped = False
            elif quote == '"' and ch == "\\":
                escaped = True
            elif ch == quote:
                if quote == "'" and i + 1 < len(text) and text[i + 1] == "'":
                    i += 1
                else:
                    quote = None
        elif ch in "'\"" and (i == 0 or text[i - 1] in " [{,:-"):
            quote = ch
        elif ch == "#" and (i == 0 or text[i - 1].isspace()):
            return text[:i].rstrip()
        i += 1
    return text.rstrip()


def parse_profile(text):
    lines, document_seen = [], False
    for number, raw in enumerate(text.splitlines(), 1):
        line = strip_comment(raw)
        if not line.strip():
            continue
        if line.strip() == "---":
            if lines or document_seen:
                raise ProfileError("multiple_documents", number, True)
            document_seen = True
            continue
        indent = len(line) - len(line.lstrip(" "))
        if "\t" in line[:len(line) - len(line.lstrip())] or indent % 2:
            raise ProfileError("use_two_space_indentation", number)
        lines.append((indent, line.strip(), number))
    if not lines or lines[0][0] != 0:
        raise ProfileError("missing_root_mapping")

    def block(index, indent, depth=0):
        if depth > 32:
            raise ProfileError("nesting_limit", unsupported=True)
        sequence = lines[index][1].startswith("- ") or lines[index][1] == "-"
        result = [] if sequence else {}
        while index < len(lines) and lines[index][0] == indent:
            _, body, number = lines[index]
            is_item = body.startswith("- ") or body == "-"
            if sequence != is_item:
                raise ProfileError("mixed_mapping_and_sequence", number)
            index += 1
            if sequence:
                body = body[1:].strip()
                mapping = bool(re.match(r"^[\w-]+:(?:\s|$)", body))
                if mapping:
                    key, rest = pair(body)
                    item = {key: scalar(rest)}
                    if not rest and index < len(lines) and lines[index][0] > indent + 2:
                        if lines[index][0] != indent + 4:
                            raise ProfileError("unexpected_indentation", lines[index][2])
                        item[key], index = block(index, indent + 4, depth + 1)
                    if index < len(lines) and lines[index][0] == indent + 2:
                        more, index = block(index, indent + 2, depth + 1)
                        if not isinstance(more, dict) or set(item) & set(more):
                            raise ProfileError("duplicate_or_misplaced_key", number)
                        item.update(more)
                elif not body and index < len(lines) and lines[index][0] == indent + 2:
                    item, index = block(index, indent + 2, depth + 1)
                else:
                    item = scalar(body)
                result.append(item)
            else:
                key, rest = pair(body)
                if key in result:
                    raise ProfileError("duplicate_key", number)
                value = scalar(rest)
                if not rest and index < len(lines) and lines[index][0] == indent + 2:
                    value, index = block(index, indent + 2, depth + 1)
                result[key] = value
            if index < len(lines) and lines[index][0] > indent:
                raise ProfileError("unexpected_indentation", lines[index][2])
        return result, index

    data, consumed = block(0, 0)
    if consumed != len(lines) or not isinstance(data, dict):
        raise ProfileError("profile_must_be_one_mapping")
    return data


def get(data, path):
    for key in path.split("."):
        if not isinstance(data, dict) or key not in data:
            return None
        data = data[key]
    return data


def validate_profile(data):
    """Validate the template's structural types, not house readiness or permission to act."""
    if not isinstance(data, dict):
        raise ProfileError("profile_must_be_one_mapping")
    if type(data.get("kit_version")) is not int or data["kit_version"] not in (1, 2, 3):
        raise ProfileError("unsupported_kit_version", unsupported=True)
    mappings = ("setup", "profile", "setup.network", "setup.agent", "setup.agent_access",
                "setup.budget", "profile.topics", "profile.house_words", "profile.house_words.nicknames",
                "profile.devices", "profile.priorities", "profile.rhythm", "profile.rhythm.wake",
                "profile.rhythm.bed", "profile.rhythm.quiet_hours", "profile.notifications",
                "profile.voice", "profile.voice.per_area", "profile.agent", "profile.operations",
                "profile.documentation")
    for name in mappings:
        if not isinstance(get(data, name), dict):
            raise ProfileError("required_mapping_missing_or_wrong_type")
    for name in ("setup.done", "profile.done", "setup.agent_access.admin", "setup.agent.usage_probe",
                 "profile.notifications.life_safety_everyone", "profile.agent.unattended",
                 "profile.documentation.manual"):
        if type(get(data, name)) is not bool:
            raise ProfileError("required_boolean_missing_or_wrong_type")
    if data.get("timezone") is not None and not isinstance(data["timezone"], str):
        raise ProfileError("timezone_must_be_text_or_null")
    lists = ("assumed", "setup.owned_devices", "setup.radios", "setup.voice",
             "setup.notification_channels", "setup.phone_platforms", "profile.people", "profile.areas",
             "profile.pets", "profile.house_words.presence_modes", "profile.house_words.modes",
             "profile.house_words.reserved", "profile.devices.integrations", "profile.devices.owned",
             "profile.devices.planned", "profile.devices.safety_relevant", "profile.priorities.order",
             "profile.priorities.never", "profile.priorities.must_work_without_ha",
             "profile.rhythm.home_in_the_day", "profile.notifications.classes", "profile.notifications.events",
             "profile.notifications.sitter_gets", "profile.notifications.speech_surfaces",
             "profile.voice.assistants", "profile.voice.exposure", "profile.agent.may",
             "profile.agent.ask_first", "profile.agent.never", "profile.operations.freezes",
             "profile.operations.backup_tiers")
    for name in lists:
        if not isinstance(get(data, name), list):
            raise ProfileError("required_list_missing_or_wrong_type")
    if not all(isinstance(item, str) for item in data["assumed"]):
        raise ProfileError("assumed_paths_must_be_text")
    for name in ("profile.people", "profile.areas"):
        if not all(isinstance(item, dict) for item in get(data, name)):
            raise ProfileError("profile_list_items_must_be_mappings")
    for name in ("router_control", "wired", "wifi_24ghz", "ipv6", "mdns_ok"):
        value = get(data, "setup.network." + name)
        if value is not None and type(value) is not bool:
            raise ProfileError("network_value_must_be_boolean_or_null")
    for name in ("setup.standing_rules",):
        value = get(data, name)
        if value is not None and (not isinstance(value, list) or
                                  not all(isinstance(item, str) for item in value)):
            raise ProfileError("standing_rules_must_be_text_list")
    for person in get(data, "profile.people"):
        for name in ("minor", "counts_for_presence", "assumed"):
            if name in person and type(person[name]) is not bool:
                raise ProfileError("person_boolean_invalid")
        level = person.get("notify_level")
        if level is not None and (type(level) is not int or not 0 <= level <= 3):
            raise ProfileError("notification_level_invalid")
        if person.get("label") is not None and not isinstance(person["label"], str):
            raise ProfileError("person_label_must_be_text_or_null")
    for area in get(data, "profile.areas"):
        if area.get("name") is not None and not isinstance(area["name"], str):
            raise ProfileError("area_name_must_be_text_or_null")
    if "adoption" in data:
        adoption = data["adoption"]
        if not isinstance(adoption, dict) or not isinstance(adoption.get("tracks"), dict):
            raise ProfileError("adoption_mapping_invalid")
        for name in ("levels_passed", "skipped", "once_done"):
            if not isinstance(adoption.get(name), list):
                raise ProfileError("adoption_list_invalid")
        for entry in adoption["levels_passed"]:
            if (not isinstance(entry, dict) or type(entry.get("level")) is not int
                    or not 0 <= entry["level"] <= 7):
                raise ProfileError("adoption_level_invalid")
            try:
                datetime.date.fromisoformat(entry["on"])
            except (ValueError, TypeError, KeyError):
                raise ProfileError("adoption_date_invalid") from None
    topics = get(data, "profile.topics")
    for name in ("people", "areas", "devices", "priorities", "rhythm", "notifications",
                 "voice", "agent", "operations", "documentation"):
        if topics.get(name) not in ("pending", "done", "assumed"):
            raise ProfileError("topic_state_missing_or_invalid")
    for name in ("buffer_pct", "away_buffer_pct"):
        value = get(data, "setup.budget." + name)
        if type(value) not in (int, float) or not 0 <= value <= 100:
            raise ProfileError("budget_percentage_invalid")
    for name in ("items_per_session", "runs_per_day"):
        value = get(data, "setup.budget." + name)
        if type(value) is not int or value < 0:
            raise ProfileError("budget_count_invalid")
    digest = get(data, "setup.agent_access.box_url_sha256")
    if digest is not None and (not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)):
        raise ProfileError("box_endpoint_fingerprint_invalid")
    return data


def load_profile(path):
    path = pathlib.Path(path)
    if path.name not in ("profile.yaml", "profile-template.yaml") or path.is_symlink():
        raise ProfileError("not_a_profile_file", unsupported=True)
    try:
        with path.open(encoding="utf-8") as source:
            text = source.read(1_048_577)
    except (OSError, UnicodeError):
        raise ProfileError("profile_unavailable", unsupported=True) from None
    if len(text) > 1_048_576:
        raise ProfileError("profile_size_limit", unsupported=True)
    return validate_profile(parse_profile(text))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", nargs="?", default="house/profile.yaml")
    args = parser.parse_args(argv)
    try:
        data = load_profile(args.profile)
    except ProfileError as error:
        print(json.dumps({"status": "unknown" if error.unsupported else "invalid",
                          "reason": error.reason, "line": error.line, "readiness": "not_checked"}))
        return 2 if error.unsupported else 1
    print(json.dumps({"status": "valid_shape", "kit_version": data["kit_version"], "readiness": "not_checked"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
