from datasets import load_dataset

# Resume-JD fit benchmark
fit = load_dataset("cnamuangtoun/resume-job-description-fit")
fit.save_to_disk("data/raw/resume_jd_fit")

# Resume classification set (larger resume pool)
atlas = load_dataset("ahmedheakl/resume-atlas")
atlas.save_to_disk("data/raw/resume_atlas")

# Skill extraction (for evaluating your JD parser)
skillspan = load_dataset("jjzha/skillspan")
skillspan.save_to_disk("data/raw/skillspan")

print("done")