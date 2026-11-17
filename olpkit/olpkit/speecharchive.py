"""Publish the source material for maintaining an accessible textbook's formula readings."""
import json
from pathlib import Path
import re
from zipfile import ZipFile

from .assembly import digest, json_bytes
from .build import load_build_product
from .cache import relative_path
from .formulaspeech import add_speech_attribution, bind_speech
from .schemas import validate_schema
from .sourceexport import deterministic_zip
from .speechreplay import replay_labels
from .syncaccept import save_acceptance


def maintenance_inputs(reader, update, released_labels, expected_reader):
    update = Path(update)
    packet = (update / "speech-input.json").read_bytes()
    store = json.loads((update / "speech-store.json").read_bytes())
    sources = (update / "occurrence-sources.json").read_bytes()
    if store.get("occurrence_source_map_sha256") != digest(sources):
        raise ValueError("The occurrence source map differs from the reviewed speech store")
    for rule in store["rules"].values():
        for passage in rule["canon_passages"]:
            for key in ("consultation_mr", "consultation", "consulted_date", "model_observed_at"):
                passage.pop(key, None)
    public_store = json_bytes(store)
    bound, _ = bind_speech(reader, packet, public_store)
    reproduced, _ = replay_labels(reader, released_labels)
    attribution = store["interface"]["attribution"]
    if (attribution != released_labels["attribution"] or bound != reproduced
            or digest(add_speech_attribution(bound, attribution)) != expected_reader):
        raise ValueError("Speech maintenance inputs differ from the released reader")
    return {"reader.html": reader, "speech-input.json": packet, "speech-store.json": public_store,
            "occurrence-sources.json": sources}


def package_speech_inputs(release_path, reader_path, update, destination):
    release_path = Path(release_path)
    release = json.loads(release_path.read_bytes())
    validate_schema("release", release)
    assets = [row for row in release["assets"] if row["format"] == "ZIP"
              and {"HTML", "EPUB"} <= set(row.get("source_for", []))]
    if len(assets) != 1:
        raise ValueError("Expected the editable source ZIP for this release's HTML and EPUB")
    asset = assets[0]
    archive = release_path.parent / relative_path(asset["name"])
    if archive.stat().st_size != asset["bytes"] or digest(archive.read_bytes()) != asset["sha256"]:
        raise ValueError("The editable source ZIP differs from the release manifest")
    with ZipFile(archive) as bundle:
        edition = json.loads(bundle.read("WEB-EDITION.json"))
        labels_bytes = bundle.read("web/speech.json")
        if edition["inputs"].get("web/speech.json") != digest(labels_bytes):
            raise ValueError("The speech labels differ from the web edition manifest")
        labels = json.loads(labels_bytes)
    files = maintenance_inputs(Path(reader_path).read_bytes(), update, labels,
                               edition["outputs"]["reader.html"])
    _, book = load_build_product(release["product_group"])
    store = json.loads(files["speech-store.json"])
    metadata = {
        "schema": "openlogic.speech-maintenance-inputs.v1", "edition": release["edition"],
        "product": book["id"], "release_tag": release["tag"], "source_url": asset["url"],
        "source_zip_sha256": asset["sha256"], "occurrences": len(labels["labels"]),
        "attribution": store["interface"]["attribution"],
        "members": {name: {"bytes": len(data), "sha256": digest(data)} for name, data in files.items()},
    }
    files["sources.json"] = json_bytes(metadata)
    for name, contents in files.items():
        if re.search(rb"(?i)(?<![A-Za-z])[A-Z]:[\\/]|/Users/|/home/|file://|github_pat_[a-z0-9_]{14,}|gh[pousr]_[a-z0-9]{12,}", contents):
            raise ValueError("Private data in the maintenance input " + name)
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    save_acceptance(path, deterministic_zip(files))
    print(f"{metadata['occurrences']} released formula readings with their occurrence and canon evidence")
    return 0
