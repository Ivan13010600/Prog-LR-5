import os
import shutil
def clean_project():
    files_to_remove = ["L5.csv", "sorted_py.txt", "sorted_c.txt"]
    dirs_to_remove = ["temp_chunks", "temp_chunks_c"]
    removed = []
    errors = []
    for f in files_to_remove:
        try:
            if os.path.exists(f):
                os.remove(f)
                removed.append(f)
        except Exception as e:
            errors.append("Failed to delete %s: %s" % (f, str(e)))
    for d in dirs_to_remove:
        try:
            if os.path.exists(d):
                shutil.rmtree(d)
                removed.append(d + "/")
        except Exception as e:
            errors.append("Failed to delete dir %s: %s" % (d, str(e)))
    print("=== Project Cleanup Report ===")
    if removed:
        print("Removed: %s" % ", ".join(removed))
    else:
        print("Nothing to remove.")
    if errors:
        print("Errors: %s" % ", ".join(errors))
    print("Done.")
if __name__ == "__main__":
    clean_project()