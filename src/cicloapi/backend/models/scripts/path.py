from pathlib import Path

BASE_DIR = (
    Path(__file__).resolve().parents[1]
)  # This goes up two levels to the project root
API_DIR = Path(__file__).resolve().parents[3]
# Define paths dictionary relative to BASE_DIR
PATH = {
    "parameters": BASE_DIR / "parameters",
    "data": BASE_DIR / "bikenwgrowth_external" / "data",
    "plots": BASE_DIR / "bikenwgrowth_external" / "plots",
    "plots_networks": BASE_DIR / "bikenwgrowth_external" / "plotsnetworks",
    "results": BASE_DIR / "bikenwgrowth_external" / "results",
    "results_constricted": BASE_DIR / "bikenwgrowth_external" / "results_constricted",
    "videos": BASE_DIR / "bikenwgrowth_external" / "videos",
    "exports": BASE_DIR / "bikenwgrowth_external" / "exports",
    "exports_json": BASE_DIR / "bikenwgrowth_external" / "exports_json",
    "logs": BASE_DIR / "bikenwgrowth_external" / "logs",
    "task_output": API_DIR / "data" / "endpoints",
}

for path in PATH.values():
    path.mkdir(parents=True, exist_ok=True)

# Example usage of a path
# print("Current working directory:", Path.cwd())
# print("Loaded PATH:", PATH)
