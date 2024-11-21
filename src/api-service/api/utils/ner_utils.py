# src/api-service/api/utils/ner_utils.py
def convert_ner_entities_to_list(text, entities: list[dict]) -> list[str]:
    ents = []
    for ent in entities:
        e = {
            "start": ent["start"],
            "end": ent["end"],
            "label": ent["entity_group"],
        }
        if (
            ents
            and -1 <= ent["start"] - ents[-1]["end"] <= 1
            and ents[-1]["label"] == e["label"]
        ):
            ents[-1]["end"] = e["end"]
            continue
        ents.append(e)

    return [text[e["start"]: e["end"]] for e in ents]