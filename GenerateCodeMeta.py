import json

def parse_requirements(path="requirements.txt"):
    deps = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if "==" in line:
                name, version = line.split("==")
                deps.append({
                    "@type": "SoftwareApplication",
                    "name": name,
                    "version": version,
                    "identifier": f"https://pypi.org/project/{name}/{version}/"
                })
    return deps

codemeta = {
    "@context": "https://doi.org/10.5063/schema/codemeta-2.0",
    "@type": "SoftwareSourceCode",
    "name": "Vienna Weather Wet-Month Prediction",
    "version": "2.0.0",
    "description": "A machine learning experiment predicting wet months from historical weather observations recorded at the Hohe Warte meteorological station in Vienna, Austria (since 1872). The pipeline covers data ingestion from DBRepo, feature engineering, model training, and evaluation.",
    "dateCreated": "2026-01-01",
    "dateModified": "2026-05-23",
    "codeRepository": "https://github.com/Emina1998/Vienna-Weather-Wet-Month-Prediction",
    "license": "MIT",
    "programmingLanguage": {
        "@type": "ComputerLanguage",
        "name": "Python",
        "version": "3.10",
        "url": "https://www.python.org/"
    },
    "runtimePlatform": "CPython 3.10",
    "operatingSystem": "Linux, macOS, Windows",
    "readme": "https://github.com/Emina1998/Vienna-Weather-Wet-Month-Prediction/blob/main/README.md",
    "author": [
        {
            "@type": "Person",
            "givenName": "Azra",
            "familyName": "Sisic",
            "@id": "https://orcid.org/0009-0006-0701-5821"
        },
        {
            "@type": "Person",
            "givenName": "Raja",
            "familyName": "Shahroz",
            "@id": "https://orcid.org/0009-0003-5130-1049"
        },
        {
            "@type": "Person",
            "givenName": "Emina",
            "familyName": "Skrijelj",
            "@id": "https://orcid.org/0009-0002-0794-5341"
        },
        {
            "@type": "Person",
            "givenName": "Kerim",
            "familyName": "Halilovic",
            "@id": "https://orcid.org/0009-0001-9615-5191"
        }
    ],
    "softwareRequirements": parse_requirements("requirements.txt"),
    "keywords": [
        "weather",
        "machine learning",
        "precipitation prediction",
        "Vienna",
        "Hohe Warte",
        "FAIR data",
        "climate"
    ],
    "developmentStatus": "active"
}

with open("codemeta.json", "w") as f:
    json.dump(codemeta, f, indent=2)

print("codemeta.json generated successfully.")
