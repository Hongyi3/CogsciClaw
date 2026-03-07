from __future__ import annotations

from collections import defaultdict
import random
from typing import Any, Dict, List


DEMO_SEED = 314159
FIXATION_DURATION_MS = 500
RESPONSE_DEADLINE_MS = 1500
INTER_TRIAL_INTERVAL_MS = 750

TRIAL_TYPES = (
    {
        "condition": "congruent",
        "trial_type": "congruent-left",
        "target_direction": "left",
        "flanker_direction": "left",
        "stimulus": "<<<<<",
        "correct_direction": "left",
    },
    {
        "condition": "congruent",
        "trial_type": "congruent-right",
        "target_direction": "right",
        "flanker_direction": "right",
        "stimulus": ">>>>>",
        "correct_direction": "right",
    },
    {
        "condition": "incongruent",
        "trial_type": "incongruent-left",
        "target_direction": "left",
        "flanker_direction": "right",
        "stimulus": ">><>>",
        "correct_direction": "left",
    },
    {
        "condition": "incongruent",
        "trial_type": "incongruent-right",
        "target_direction": "right",
        "flanker_direction": "left",
        "stimulus": "<<><<",
        "correct_direction": "right",
    },
)

PARTICIPANTS = (
    {
        "participant_id": "demo001",
        "session_id": "1",
        "mapping_variant": "A",
        "response_mapping": {"left": "f", "right": "j"},
        "rt_offset_ms": 0,
    },
    {
        "participant_id": "demo002",
        "session_id": "1",
        "mapping_variant": "B",
        "response_mapping": {"left": "j", "right": "f"},
        "rt_offset_ms": 20,
    },
)

TRIAL_COLUMN_ORDER = [
    "participant_id",
    "session_id",
    "mapping_variant",
    "trial_index",
    "condition",
    "trial_type",
    "stimulus",
    "target_direction",
    "flanker_direction",
    "correct_direction",
    "correct_response_key",
    "response_key",
    "accuracy",
    "rt_ms",
    "fixation_duration_ms",
    "response_deadline_ms",
    "inter_trial_interval_ms",
    "synthetic",
]

COLUMN_DEFINITIONS = {
    "participant_id": "Deterministic synthetic participant identifier.",
    "session_id": "Synthetic session identifier used for the demo dataset.",
    "mapping_variant": "Response-mapping variant applied to the participant.",
    "trial_index": "One-based index of the trial within the deterministic schedule.",
    "condition": "Congruent or incongruent Flanker condition label.",
    "trial_type": "Condition-specific left/right trial subtype.",
    "stimulus": "Rendered arrow stimulus string presented to the participant.",
    "target_direction": "Direction of the central target arrow.",
    "flanker_direction": "Direction of the surrounding flanker arrows.",
    "correct_direction": "Correct conceptual response direction for the target arrow.",
    "correct_response_key": "Keyboard key mapped to the correct response direction.",
    "response_key": "Synthetic keyboard response emitted for the demo dataset.",
    "accuracy": "Deterministic synthetic correctness indicator where 1 = correct and 0 = incorrect.",
    "rt_ms": "Deterministic synthetic reaction time in milliseconds.",
    "fixation_duration_ms": "Fixation duration for the trial in milliseconds.",
    "response_deadline_ms": "Stimulus response deadline in milliseconds.",
    "inter_trial_interval_ms": "Inter-trial interval in milliseconds.",
    "synthetic": "Literal indicator that the row is synthetic demo data.",
}


def demo_profile() -> Dict[str, Any]:
    return {
        "seed": DEMO_SEED,
        "task_name": "flanker",
        "supported_profile": "canonical-flanker-demo",
        "synthetic_data": True,
        "practice_block": False,
        "feedback_block": False,
        "adaptive_logic": False,
        "timing_ms": {
            "fixation": FIXATION_DURATION_MS,
            "response_deadline": RESPONSE_DEADLINE_MS,
            "inter_trial_interval": INTER_TRIAL_INTERVAL_MS,
        },
        "participants": [
            {
                "participant_id": participant["participant_id"],
                "session_id": participant["session_id"],
                "mapping_variant": participant["mapping_variant"],
                "response_mapping": participant["response_mapping"],
            }
            for participant in PARTICIPANTS
        ],
        "stimuli": [trial_type["stimulus"] for trial_type in TRIAL_TYPES],
        "trial_columns": TRIAL_COLUMN_ORDER,
        "column_definitions": COLUMN_DEFINITIONS,
    }


def build_trial_schedule(trial_count: int) -> List[Dict[str, Any]]:
    if trial_count != 160:
        raise ValueError("This milestone supports only 160 trials per participant.")

    trials: List[Dict[str, Any]] = []
    repetitions = trial_count // len(TRIAL_TYPES)
    for trial_type in TRIAL_TYPES:
        for _ in range(repetitions):
            trials.append(dict(trial_type))

    rng = random.Random(DEMO_SEED)
    rng.shuffle(trials)

    schedule: List[Dict[str, Any]] = []
    for index, trial in enumerate(trials, start=1):
        schedule.append(
            {
                "trial_index": index,
                "condition": trial["condition"],
                "trial_type": trial["trial_type"],
                "stimulus": trial["stimulus"],
                "target_direction": trial["target_direction"],
                "flanker_direction": trial["flanker_direction"],
                "correct_direction": trial["correct_direction"],
            }
        )
    return schedule


def _is_correct(condition_index: int, condition: str) -> bool:
    if condition == "congruent":
        return condition_index % 40 != 0
    return condition_index % 10 != 0


def _rt_ms(trial_index: int, condition: str, participant_offset: int, correct: bool) -> int:
    base = 480 if condition == "congruent" else 560
    jitter = ((trial_index * 17) + (participant_offset * 3)) % 41 - 20
    penalty = 35 if not correct else 0
    return base + participant_offset + jitter + penalty


def generate_synthetic_tables(schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    tables: List[Dict[str, Any]] = []

    for participant in PARTICIPANTS:
        condition_counts = defaultdict(int)
        rows: List[Dict[str, Any]] = []

        for trial in schedule:
            condition = trial["condition"]
            condition_counts[condition] += 1
            correct = _is_correct(condition_counts[condition], condition)
            response_mapping = participant["response_mapping"]
            correct_key = response_mapping[trial["correct_direction"]]
            incorrect_direction = "right" if trial["correct_direction"] == "left" else "left"
            response_key = correct_key if correct else response_mapping[incorrect_direction]

            rows.append(
                {
                    "participant_id": participant["participant_id"],
                    "session_id": participant["session_id"],
                    "mapping_variant": participant["mapping_variant"],
                    "trial_index": trial["trial_index"],
                    "condition": condition,
                    "trial_type": trial["trial_type"],
                    "stimulus": trial["stimulus"],
                    "target_direction": trial["target_direction"],
                    "flanker_direction": trial["flanker_direction"],
                    "correct_direction": trial["correct_direction"],
                    "correct_response_key": correct_key,
                    "response_key": response_key,
                    "accuracy": 1 if correct else 0,
                    "rt_ms": _rt_ms(
                        trial["trial_index"],
                        condition,
                        participant["rt_offset_ms"],
                        correct,
                    ),
                    "fixation_duration_ms": FIXATION_DURATION_MS,
                    "response_deadline_ms": RESPONSE_DEADLINE_MS,
                    "inter_trial_interval_ms": INTER_TRIAL_INTERVAL_MS,
                    "synthetic": "true",
                }
            )

        tables.append(
            {
                "participant_id": participant["participant_id"],
                "session_id": participant["session_id"],
                "mapping_variant": participant["mapping_variant"],
                "rows": rows,
            }
        )

    return tables


def summarize_schedule(schedule: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts = defaultdict(int)
    for trial in schedule:
        counts[trial["condition"]] += 1

    return {
        "trial_count": len(schedule),
        "condition_counts": dict(sorted(counts.items())),
        "mapping_variants": [participant["mapping_variant"] for participant in PARTICIPANTS],
    }
