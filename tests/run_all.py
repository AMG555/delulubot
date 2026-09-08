import sys
import pytest

def main():
    print("Running Delulubot Automated QA and A/B Test Suite...\n")
    exit_code = pytest.main(["-v", "tests"])
    if exit_code == 0:
        print("\nSUCCESS: All QA and A/B tests passed cleanly!")
    else:
        print(f"\nFAILURE: Tests failed with exit code {exit_code}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
