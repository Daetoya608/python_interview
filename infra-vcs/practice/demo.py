"""Exercise Git in a disposable repository, never in the user's repository."""
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory


def main():
    with TemporaryDirectory(prefix="git-interview-") as temp:
        repo = Path(temp)

        def git(*args, expected=0):
            result = subprocess.run(
                ["git", "-c", f"safe.directory={repo.as_posix()}",
                 "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                 *args], cwd=repo, capture_output=True, text=True, encoding="utf-8",
            )
            assert result.returncode == expected, (args, result.stdout, result.stderr)
            return result.stdout.strip()

        git("init", "-b", "main")
        git("config", "--local", "user.name", "Study Example")
        git("config", "--local", "user.email", "study@example.test")
        file = repo / "note.txt"
        file.write_text("base\n", encoding="utf-8")
        git("add", "note.txt")
        git("commit", "-m", "docs: add base note")
        git("switch", "-c", "feature")
        file.write_text("feature\n", encoding="utf-8")
        git("commit", "-am", "docs: change note in feature")
        git("switch", "main")
        file.write_text("main\n", encoding="utf-8")
        git("commit", "-am", "docs: change note in main")
        git("merge", "feature", expected=1)
        assert "UU note.txt" in git("status", "--short")
        file.write_text("main + feature\n", encoding="utf-8")
        git("add", "note.txt")
        git("commit", "-m", "docs: resolve both changes")
        file.write_text("temporary change\n", encoding="utf-8")
        git("commit", "-am", "docs: introduce a change to revert")
        git("revert", "--no-edit", "HEAD")
        assert file.read_text(encoding="utf-8") == "main + feature\n"
        assert git("status", "--porcelain") == ""
        print(git("log", "--oneline", "--graph", "--all"))
        print("Conflict resolved; revert restored content; temporary repo is clean.")


if __name__ == "__main__":
    main()
