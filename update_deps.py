import subprocess


def main():
    # Using 'with' allows for file to close when done, even with exceptions.
    with open("requirements.txt", 'r') as req_file:
        for req in req_file:
            subprocess.run(["pip", "install", "--upgrade", req.strip()])
            print()
    return


if __name__ == "__main__":
    main()
