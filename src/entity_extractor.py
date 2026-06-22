import spacy

# Load once when app starts
nlp = spacy.load("en_core_web_sm")


def extract_entities(text):
    """
    Extract named entities from text.
    """

    doc = nlp(text)

    entities = {
        "people": [],
        "organizations": [],
        "locations": [],
        "dates": []
    }

    for ent in doc.ents:

        if ent.label_ == "PERSON":
            entities["people"].append(ent.text)

        elif ent.label_ == "ORG":
            entities["organizations"].append(ent.text)

        elif ent.label_ in ["GPE", "LOC"]:
            entities["locations"].append(ent.text)

        elif ent.label_ == "DATE":
            entities["dates"].append(ent.text)

    # Remove duplicates

    for key in entities:
        entities[key] = list(
            set(entities[key])
        )

    return entities