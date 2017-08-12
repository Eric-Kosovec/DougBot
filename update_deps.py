import subprocess


def main():
    # Using 'with' allows for file to close when done, even with exceptions.
    with open("deps.txt", 'r') as f:
        for dep in f:
            subprocess.run(["pip", "install", "--upgrade", dep.strip()])
            print()
    return


if __name__ == "__main__":
    main()
