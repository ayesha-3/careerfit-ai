import json, pandas as pd
from pathlib import Path
from datasets import load_from_disk

ds = load_from_disk("data/raw/resume_jd_fit")
df = pd.concat([ds["train"].to_pandas(), ds["test"].to_pandas()])
print(df.label.unique())   # check the exact label strings first

df["rw"] = df.resume_text.str.split().str.len()
df["jw"] = df.job_description_text.str.split().str.len()
df = df[df.rw.between(150, 900) & df.jw.between(150, 700)]   # keep annotation time sane
df = df.drop_duplicates("resume_text").drop_duplicates("job_description_text")

plan = [("Good Fit", 7), ("Potential Fit", 7), ("No Fit", 6)]  # edit if labels differ
picked = pd.concat([df[df.label == l].sample(n, random_state=42) for l, n in plan])

rows = []
for i, (_, r) in enumerate(picked.sample(frac=1, random_state=1).iterrows(), 1):
    pid = f"p{i:02d}"
    d = Path(f"data/gold/pairs/{pid}"); d.mkdir(parents=True, exist_ok=True)
    (d / "resume.txt").write_text(r.resume_text, encoding="utf-8")
    (d / "jd.txt").write_text(r.job_description_text, encoding="utf-8")
    (d / "meta.json").write_text(json.dumps({"source": "resume_jd_fit", "dataset_label": r.label}))
    rows.append({"pair_id": pid, "source": "resume_jd_fit", "dataset_label": r.label})
pd.DataFrame(rows).to_csv("data/gold/manifest.csv", index=False)