from pathlib import Path

def failure_artifact_path(test_name : str, attempt : int):
   path = Path("test-results")/test_name/f"attempt-{attempt}"
   path.mkdir(parents=True, exist_ok = True)
   return path

print(failure_artifact_path("test_login", 2))