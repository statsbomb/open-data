"""
StatsBomb Open Data Validator
Validates JSON files for common data quality issues.
Covers: events, matches, lineups, competitions data.
References: StatsBomb Data Specification v1.1
"""

import json
import os
import sys
import re
from pathlib import Path


# Constants from the spec

PITCH_X_MIN, PITCH_X_MAX = 0, 120
PITCH_Y_MIN, PITCH_Y_MAX = 0, 80

VALID_PERIODS = {1, 2, 3, 4, 5}
VALID_DATA_VERSIONS = {"1.0.0", "1.0.1", "1.0.2", "1.0.3", "1.1.0"}
VALID_PLAY_PATTERN_IDS = set(range(1, 10))  # 1–9

VALID_COMPETITION_STAGE_IDS = {
    1, 2, 6, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19,
    20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 33, 34, 35
}

# Event type IDs from spec
CARRY_TYPE_ID    = 43
PASS_TYPE_ID     = 30
SHOT_TYPE_ID     = 16
DUEL_TYPE_ID     = 4
SUB_TYPE_ID      = 19
CLEARANCE_ID     = 9
GOALKEEPER_ID    = 23

TIMESTAMP_PATTERN = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3}$")
DATE_PATTERN      = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_PATTERN      = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3}$")


# Helpers
class Issue:
    def __init__(self, file_path, level, check, detail):
        self.file_path = str(file_path)
        self.level     = level   
        self.check     = check
        self.detail    = detail

    def __str__(self):
        short = os.path.basename(self.file_path)
        return f"  [{self.level}] {short} | {self.check}: {self.detail}"


def load_json(path):
    """Load a JSON file, checking for null bytes first."""
    raw = Path(path).read_bytes()
    if b"\x00" in raw:
        return None, "null bytes found (corrupted file)"
    try:
        return json.loads(raw.decode("utf-8")), None
    except json.JSONDecodeError as e:
        return None, f"JSON parse error: {e}"


def coord_ok(loc):
    """Return True if [x, y] is within pitch bounds."""
    if not isinstance(loc, list) or len(loc) < 2:
        return False
    x, y = loc[0], loc[1]
    return (PITCH_X_MIN <= x <= PITCH_X_MAX and
            PITCH_Y_MIN <= y <= PITCH_Y_MAX)


#  Per-file validators

def validate_competitions(path):
    issues = []
    data, err = load_json(path)
    if err:
        issues.append(Issue(path, "ERROR", "corrupt_file", err))
        return issues

    if not isinstance(data, list):
        issues.append(Issue(path, "ERROR", "structure", "root should be a list"))
        return issues

    for i, comp in enumerate(data):
        ref = f"entry[{i}]"
        for field in ("competition_id", "season_id", "competition_name",
                      "season_name", "competition_gender"):
            if field not in comp:
                issues.append(Issue(path, "ERROR", "missing_field",
                                    f"{ref} missing '{field}'"))

        gender = comp.get("competition_gender")
        if gender and gender not in ("male", "female"):
            issues.append(Issue(path, "ERROR", "invalid_gender",
                                f"{ref} competition_gender='{gender}' "
                                f"(expected 'male' or 'female')"))

    return issues


def validate_match_file(path):
    issues = []
    data, err = load_json(path)
    if err:
        issues.append(Issue(path, "ERROR", "corrupt_file", err))
        return issues

    if not isinstance(data, list):
        issues.append(Issue(path, "ERROR", "structure", "root should be a list"))
        return issues

    home_manager_counts = {}
    away_manager_counts = {}

    for match in data:
        mid = match.get("match_id", "?")
        ref = f"match_id={mid}"

        # Required fields
        for field in ("match_id", "match_date", "kick_off",
                      "home_team", "away_team", "home_score", "away_score"):
            if field not in match:
                issues.append(Issue(path, "ERROR", "missing_field",
                                    f"{ref} missing '{field}'"))

        # Date / time formats
        md = match.get("match_date", "")
        if md and not DATE_PATTERN.match(str(md)):
            issues.append(Issue(path, "WARNING", "bad_date_format",
                                f"{ref} match_date='{md}'"))

        ko = match.get("kick_off", "")
        if ko and not TIME_PATTERN.match(str(ko)):
            issues.append(Issue(path, "WARNING", "bad_time_format",
                                f"{ref} kick_off='{ko}'"))

        # Scores
        for score_field in ("home_score", "away_score"):
            val = match.get(score_field)
            if val is not None and (not isinstance(val, int) or val < 0):
                issues.append(Issue(path, "ERROR", "invalid_score",
                                    f"{ref} {score_field}={val}"))

        # Competition stage
        stage = match.get("competition_stage", {})
        stage_id = stage.get("id") if isinstance(stage, dict) else None
        if stage_id is not None and stage_id not in VALID_COMPETITION_STAGE_IDS:
            issues.append(Issue(path, "WARNING", "unknown_competition_stage",
                                f"{ref} competition_stage.id={stage_id}"))

        # Data version
        meta = match.get("metadata", {})
        if isinstance(meta, dict):
            dv = meta.get("data_version")
            if dv and dv not in VALID_DATA_VERSIONS:
                issues.append(Issue(path, "WARNING", "unknown_data_version",
                                    f"{ref} data_version='{dv}'"))

        # Team name consistency: team vs possession_team equivalent
        ht = match.get("home_team", {})
        at = match.get("away_team", {})
        if isinstance(ht, dict) and isinstance(at, dict):
            if ht.get("home_team_id") == at.get("away_team_id"):
                issues.append(Issue(path, "ERROR", "team_id_collision",
                                    f"{ref} home and away team share same id"))

        # Duplicate managers
        home_mgr = match.get("home_team", {})
        if isinstance(home_mgr, dict):
            mgr_list = home_mgr.get("managers", [])
            if isinstance(mgr_list, list) and len(mgr_list) > 1:
                ids = [m.get("id") for m in mgr_list]
                if len(ids) != len(set(ids)):
                    issues.append(Issue(path, "ERROR", "duplicate_manager",
                                        f"{ref} home_team has duplicate managers"))
            home_manager_counts[mid] = len(mgr_list) if isinstance(mgr_list, list) else 0

        away_mgr = match.get("away_team", {})
        if isinstance(away_mgr, dict):
            mgr_list = away_mgr.get("managers", [])
            if isinstance(mgr_list, list) and len(mgr_list) > 1:
                ids = [m.get("id") for m in mgr_list]
                if len(ids) != len(set(ids)):
                    issues.append(Issue(path, "ERROR", "duplicate_manager",
                                        f"{ref} away_team has duplicate managers"))

    return issues


def validate_lineup_file(path):
    issues = []
    data, err = load_json(path)
    if err:
        issues.append(Issue(path, "ERROR", "corrupt_file", err))
        return issues

    if not isinstance(data, list):
        issues.append(Issue(path, "ERROR", "structure", "root should be a list"))
        return issues

    for team_entry in data:
        team_name = team_entry.get("team_name", "?")
        lineup = team_entry.get("lineup", [])

        if not isinstance(lineup, list):
            continue

        seen_ids      = set()

        for player in lineup:
            pid    = player.get("player_id")
            jersey = player.get("jersey_number")
            name   = player.get("player_name", "?")
            ref    = f"team={team_name} player={name}"

            # Required fields
            for field in ("player_id", "player_name", "jersey_number", "country"):
                if field not in player:
                    issues.append(Issue(path, "ERROR", "missing_field",
                                        f"{ref} missing '{field}'"))

            # Duplicate player IDs within same team
            if pid is not None:
                if pid in seen_ids:
                    issues.append(Issue(path, "ERROR", "duplicate_player_id",
                                        f"{ref} player_id={pid} duplicated"))
                seen_ids.add(pid)

            # Country object
            country = player.get("country")
            if country and isinstance(country, dict):
                if "id" not in country or "name" not in country:
                    issues.append(Issue(path, "WARNING", "incomplete_country",
                                        f"{ref} country object missing id or name"))

    return issues


def validate_event_file(path):
    issues = []
    data, err = load_json(path)
    if err:
        issues.append(Issue(path, "ERROR", "corrupt_file", err))
        return issues

    if not isinstance(data, list):
        issues.append(Issue(path, "ERROR", "structure", "root should be a list"))
        return issues

    seen_event_ids = set()

    for event in data:
        eid  = event.get("id", "?")
        ref  = f"event_id={eid}"

        # Duplicate event IDs
        if eid != "?" and eid in seen_event_ids:
            issues.append(Issue(path, "ERROR", "duplicate_event_id",
                                f"{ref} event id appears more than once"))
        seen_event_ids.add(eid)

        # Period
        period = event.get("period")
        if period is not None and period not in VALID_PERIODS:
            issues.append(Issue(path, "ERROR", "invalid_period",
                                f"{ref} period={period} (valid: 1–5)"))

        # Timestamp format
        ts = event.get("timestamp", "")
        if ts and not TIMESTAMP_PATTERN.match(str(ts)):
            issues.append(Issue(path, "WARNING", "bad_timestamp",
                                f"{ref} timestamp='{ts}'"))

        # Second value
        second = event.get("second")
        if second is not None and not (0 <= second <= 59):
            issues.append(Issue(path, "WARNING", "invalid_second",
                                f"{ref} second={second}"))

        # Play pattern
        pp = event.get("play_pattern", {})
        pp_id = pp.get("id") if isinstance(pp, dict) else None
        if pp_id is not None and pp_id not in VALID_PLAY_PATTERN_IDS:
            issues.append(Issue(path, "WARNING", "invalid_play_pattern",
                                f"{ref} play_pattern.id={pp_id}"))

        # Location bounds
        loc = event.get("location")
        if loc is not None:
            if not isinstance(loc, list) or len(loc) < 2:
                issues.append(Issue(path, "ERROR", "malformed_location",
                                    f"{ref} location is not a valid [x,y] array"))
            elif not coord_ok(loc):
                issues.append(Issue(path, "ERROR", "location_out_of_bounds",
                                    f"{ref} location={loc} outside pitch bounds "
                                    f"(x:0–120, y:0–80)"))

        # Event type id
        etype = event.get("type", {})
        etype_id = etype.get("id") if isinstance(etype, dict) else None

        # Event-type-specific checks

        if etype_id == CARRY_TYPE_ID:
            carry = event.get("carry", {})
            end_loc = carry.get("end_location") if isinstance(carry, dict) else None
            if end_loc is None:
                issues.append(Issue(path, "ERROR", "missing_carry_end_location",
                                    f"{ref} Carry event missing carry.end_location"))
            elif not coord_ok(end_loc):
                issues.append(Issue(path, "ERROR", "carry_end_out_of_bounds",
                                    f"{ref} carry.end_location={end_loc} out of bounds"))

        if etype_id == PASS_TYPE_ID:
            pass_data = event.get("pass", {})
            if isinstance(pass_data, dict):
                for required in ("length", "angle", "end_location"):
                    if required not in pass_data:
                        issues.append(Issue(path, "ERROR", "missing_pass_field",
                                            f"{ref} Pass missing pass.{required}"))
                end_loc = pass_data.get("end_location")
                if end_loc and not coord_ok(end_loc):
                    issues.append(Issue(path, "ERROR", "pass_end_out_of_bounds",
                                        f"{ref} pass.end_location={end_loc} out of bounds"))

        if etype_id == SHOT_TYPE_ID:
            shot = event.get("shot", {})
            if isinstance(shot, dict):
                xg = shot.get("statsbomb_xg")
                if xg is None:
                    issues.append(Issue(path, "WARNING", "missing_xg",
                                        f"{ref} Shot missing statsbomb_xg"))
                elif not (0.0 <= xg <= 1.0):
                    issues.append(Issue(path, "ERROR", "xg_out_of_range",
                                        f"{ref} statsbomb_xg={xg} not in [0,1]"))

        if etype_id == DUEL_TYPE_ID:
            duel = event.get("duel", {})
            if isinstance(duel, dict) and "type" not in duel:
                issues.append(Issue(path, "ERROR", "missing_duel_type",
                                    f"{ref} Duel event missing duel.type"))

        if etype_id == SUB_TYPE_ID:
            sub = event.get("substitution", {})
            if isinstance(sub, dict):
                if "replacement" not in sub:
                    issues.append(Issue(path, "ERROR", "missing_sub_replacement",
                                        f"{ref} Substitution missing replacement"))
                if "outcome" not in sub:
                    issues.append(Issue(path, "WARNING", "missing_sub_outcome",
                                        f"{ref} Substitution missing outcome"))

        # team vs possession_team name mismatch
        team      = event.get("team", {})
        poss_team = event.get("possession_team", {})
        if (isinstance(team, dict) and isinstance(poss_team, dict)
                and team.get("id") == poss_team.get("id")
                and team.get("name") != poss_team.get("name")):
            issues.append(Issue(path, "ERROR", "team_name_mismatch",
                                f"{ref} team.name='{team.get('name')}' != "
                                f"possession_team.name='{poss_team.get('name')}'"))

    return issues


def validate_threesixty_file(path):
    issues = []
    data, err = load_json(path)
    if err:
        issues.append(Issue(path, "ERROR", "corrupt_file", err))
        return issues

    if not isinstance(data, list):
        issues.append(Issue(path, "ERROR", "structure", "root should be a list"))
        return issues

    for frame in data:
        fid = frame.get("event_uuid", "?")
        ref = f"frame={fid}"
        freeze = frame.get("freeze_frame", [])
        if not isinstance(freeze, list):
            continue
        for player in freeze:
            loc = player.get("location")
            if loc and not coord_ok(loc):
                issues.append(Issue(path, "ERROR", "ff_location_out_of_bounds",
                                    f"{ref} freeze_frame player location={loc} "
                                    f"outside pitch bounds"))

    return issues


#  Cross-file consistency

def cross_file_checks(repo_root, all_issues):
    """Check that every match has corresponding events and lineup files."""
    matches_dir = Path(repo_root) / "matches"
    events_dir  = Path(repo_root) / "events"
    lineups_dir = Path(repo_root) / "lineups"

    if not matches_dir.exists():
        return

    for match_file in matches_dir.glob("**/*.json"):
        data, err = load_json(match_file)
        if err or not isinstance(data, list):
            continue
        for match in data:
            mid = match.get("match_id")
            if mid is None:
                continue
            if not (events_dir / f"{mid}.json").exists():
                all_issues.append(Issue(match_file, "WARNING",
                                        "missing_events_file",
                                        f"match_id={mid} has no events/{mid}.json"))
            if not (lineups_dir / f"{mid}.json").exists():
                all_issues.append(Issue(match_file, "WARNING",
                                        "missing_lineups_file",
                                        f"match_id={mid} has no lineups/{mid}.json"))


# Main runner

def run_validation(repo_root="."):
    repo  = Path(repo_root)
    all_issues = []

    file_map = {
        "competitions": (repo / "competitions.json", validate_competitions),
        "matches":      (repo / "matches",            validate_match_file),
        "lineups":      (repo / "lineups",            validate_lineup_file),
        "events":       (repo / "events",             validate_event_file),
        "three-sixty":  (repo / "three-sixty",        validate_threesixty_file),
    }

    for label, (target, validator) in file_map.items():
        if target.is_file():
            print(f"\n── Validating {label} ──")
            issues = validator(target)
            all_issues.extend(issues)
            for i in issues:
                print(i)
        elif target.is_dir():
            json_files = sorted(target.rglob("*.json"))
            print(f"\n── Validating {label} ({len(json_files)} files) ──")
            for jf in json_files:
                issues = validator(jf)
                all_issues.extend(issues)
                for i in issues:
                    print(i)

    print("\n── Cross-file consistency ──")
    cross_file_checks(repo_root, all_issues)
    for i in all_issues:
        if "missing_events_file" in i.check or "missing_lineups_file" in i.check:
            print(i)


    errors   = [i for i in all_issues if i.level == "ERROR"]
    warnings = [i for i in all_issues if i.level == "WARNING"]

    print("\n" + "=" * 60)
    print(f"VALIDATION COMPLETE")
    print(f"  Total issues : {len(all_issues)}")
    print(f"  Errors       : {len(errors)}")
    print(f"  Warnings     : {len(warnings)}")
    print("=" * 60)

    if errors:
        print("\nTop errors:")
        for e in errors[:10]:
            print(e)
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")

    return 1 if errors else 0


if __name__ == "__main__":
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    sys.exit(run_validation(repo_path))
