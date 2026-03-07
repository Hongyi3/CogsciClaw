from __future__ import annotations

import json
from pathlib import Path
from shutil import copy2
from typing import Any, Dict, List

from .flanker_demo import (
    FIXATION_DURATION_MS,
    INTER_TRIAL_INTERVAL_MS,
    RESPONSE_DEADLINE_MS,
)
from .paths import VENDOR_DIR


JSPSYCH_VERSION = "8.2.2"
HTML_KEYBOARD_PLUGIN_VERSION = "2.1.0"


def _task_index_html(study_title: str) -> str:
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{study_title}</title>
    <link rel="stylesheet" href="jspsych/jspsych.css">
    <style>
      body {{
        background: #faf8f2;
        color: #171512;
        font-family: "Iowan Old Style", "Palatino Linotype", serif;
        margin: 0;
      }}

      #task-shell {{
        max-width: 900px;
        margin: 0 auto;
        padding: 2rem 1.5rem 3rem;
      }}

      .flanker-stimulus {{
        font-family: "Courier New", monospace;
        font-size: 3rem;
        letter-spacing: 0.3rem;
      }}

      .task-summary {{
        max-width: 760px;
        margin: 0 auto;
        line-height: 1.5;
      }}

      .task-summary a {{
        color: #0f4c5c;
        display: inline-block;
        margin-right: 1rem;
        margin-top: 1rem;
      }}
    </style>
  </head>
  <body>
    <main id="task-shell"></main>
    <script src="jspsych/jspsych.js"></script>
    <script src="jspsych/plugin-html-keyboard-response.js"></script>
    <script src="task.js"></script>
  </body>
</html>
"""


def _task_javascript(
    study_title: str,
    schedule: List[Dict[str, Any]],
    profile: Dict[str, Any],
    task_metadata: Dict[str, Any],
) -> str:
    trials_json = json.dumps(schedule, indent=2, sort_keys=True)
    metadata_json = json.dumps(task_metadata, indent=2, sort_keys=True)
    profile_json = json.dumps(profile, indent=2, sort_keys=True)

    return f"""const STUDY_TITLE = {json.dumps(study_title)};
const TASK_METADATA = {metadata_json};
const DEMO_PROFILE = {profile_json};
const TRIALS = {trials_json};

function selectedMappingVariant() {{
  const params = new URLSearchParams(window.location.search);
  return params.get("mapping") === "B" ? "B" : "A";
}}

function responseMapping(variant) {{
  return TASK_METADATA.response_mappings[variant];
}}

function stimulusHtml(trial) {{
  return `<div class="flanker-stimulus">${{trial.stimulus}}</div>`;
}}

function reminderPrompt(mapping) {{
  return `Respond to the center arrow. Left = <strong>${{mapping.left}}</strong>, Right = <strong>${{mapping.right}}</strong>.`;
}}

function downloadLink(label, filename, contents, mimeType) {{
  const anchor = document.createElement("a");
  anchor.download = filename;
  anchor.href = URL.createObjectURL(new Blob([contents], {{ type: mimeType }}));
  anchor.textContent = label;
  return anchor;
}}

function renderCompletionPage(jsPsych, mappingVariant) {{
  const stimulusData = jsPsych.data.get().filter({{ trial_role: "stimulus" }});
  const accuracy = stimulusData.select("correct").mean();
  const meanRt = stimulusData.filter({{ correct: true }}).select("rt").mean();
  const shell = document.getElementById("task-shell");
  shell.innerHTML = "";

  const container = document.createElement("section");
  container.className = "task-summary";
  container.innerHTML = `
    <h1>${{STUDY_TITLE}}</h1>
    <p>This browser artifact is the deterministic jsPsych task package for the canonical Flanker demo slice.</p>
    <p>Mapping variant: <strong>${{mappingVariant}}</strong></p>
    <p>Accuracy: <strong>${{(accuracy * 100).toFixed(1)}}%</strong></p>
    <p>Mean correct RT: <strong>${{meanRt.toFixed(1)}} ms</strong></p>
    <p>Use the links below to download the live browser-run data from this task package.</p>
  `;

  container.appendChild(
    downloadLink("Download browser-run CSV", "flanker-browser-run.csv", stimulusData.csv(), "text/csv")
  );
  container.appendChild(
    downloadLink(
      "Download browser-run JSON",
      "flanker-browser-run.json",
      stimulusData.json(),
      "application/json"
    )
  );

  shell.appendChild(container);
}}

const mappingVariant = selectedMappingVariant();
const mapping = responseMapping(mappingVariant);
const jsPsych = initJsPsych({{
  display_element: document.getElementById("task-shell"),
  on_finish: function() {{
    renderCompletionPage(jsPsych, mappingVariant);
  }},
}});

const timeline = [
  {{
    type: jsPsychHtmlKeyboardResponse,
    stimulus: `
      <section class="task-summary">
        <h1>${{STUDY_TITLE}}</h1>
        <p>This package runs a deterministic Flanker task generated from a structured study spec.</p>
        <p>${{reminderPrompt(mapping)}}</p>
        <p>Press any valid response key to begin.</p>
      </section>
    `,
    choices: [mapping.left, mapping.right],
  }},
];

TRIALS.forEach((trial) => {{
  const correctKey = mapping[trial.correct_direction];

  timeline.push({{
    type: jsPsychHtmlKeyboardResponse,
    stimulus: '<div class="flanker-stimulus">+</div>',
    choices: "NO_KEYS",
    trial_duration: TASK_METADATA.timings.fixation_duration_ms,
    data: {{
      trial_role: "fixation",
      mapping_variant: mappingVariant,
      trial_index: trial.trial_index,
    }},
  }});

  timeline.push({{
    type: jsPsychHtmlKeyboardResponse,
    stimulus: stimulusHtml(trial),
    choices: [mapping.left, mapping.right],
    prompt: `<p>${{reminderPrompt(mapping)}}</p>`,
    trial_duration: TASK_METADATA.timings.response_deadline_ms,
    stimulus_duration: TASK_METADATA.timings.response_deadline_ms,
    response_ends_trial: true,
    data: Object.assign({{}}, trial, {{
      trial_role: "stimulus",
      mapping_variant: mappingVariant,
      correct_response_key: correctKey,
    }}),
    on_finish: function(data) {{
      data.correct = data.response === correctKey;
    }},
  }});

  timeline.push({{
    type: jsPsychHtmlKeyboardResponse,
    stimulus: '<div class="flanker-stimulus">&nbsp;</div>',
    choices: "NO_KEYS",
    trial_duration: TASK_METADATA.timings.inter_trial_interval_ms,
    data: {{
      trial_role: "iti",
      mapping_variant: mappingVariant,
      trial_index: trial.trial_index,
    }},
  }});
}});

jsPsych.run(timeline);
"""


def write_task_artifact(
    task_dir: Path,
    study_title: str,
    schedule: List[Dict[str, Any]],
    profile: Dict[str, Any],
    study_spec_sha256: str,
) -> Dict[str, Any]:
    task_dir.mkdir(parents=True, exist_ok=True)
    asset_dir = task_dir / "jspsych"
    asset_dir.mkdir(parents=True, exist_ok=True)

    for source_name, target_name in (
        ("jspsych.js", "jspsych.js"),
        ("jspsych.css", "jspsych.css"),
        ("plugin-html-keyboard-response.js", "plugin-html-keyboard-response.js"),
    ):
        copy2(VENDOR_DIR / source_name, asset_dir / target_name)

    task_metadata = {
        "study_title": study_title,
        "study_spec_sha256": study_spec_sha256,
        "task_name": "flanker",
        "task_artifact_type": "jspsych-browser-demo",
        "supported_profile": "canonical-flanker-demo",
        "timings": {
            "fixation_duration_ms": FIXATION_DURATION_MS,
            "response_deadline_ms": RESPONSE_DEADLINE_MS,
            "inter_trial_interval_ms": INTER_TRIAL_INTERVAL_MS,
        },
        "response_mappings": {
            "A": {"left": "f", "right": "j"},
            "B": {"left": "j", "right": "f"},
        },
        "jspsych_assets": {
            "jspsych": JSPSYCH_VERSION,
            "plugin_html_keyboard_response": HTML_KEYBOARD_PLUGIN_VERSION,
        },
        "synthetic_data_used_for_curated_demo": True,
    }

    (task_dir / "trials.json").write_text(
        json.dumps(schedule, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (task_dir / "task_metadata.json").write_text(
        json.dumps(task_metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (task_dir / "index.html").write_text(_task_index_html(study_title), encoding="utf-8")
    (task_dir / "task.js").write_text(
        _task_javascript(study_title, schedule, profile, task_metadata),
        encoding="utf-8",
    )

    return task_metadata
