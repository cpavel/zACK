from glob import glob


def fix_file():
    fields = False
    moved = False
    new_file = []
    moved_section = []
    count = 0
    filenames = glob("data/migrations/0*.py")
    filenames.sort()

    filename = filenames[-1]

    _file = open(filename, "r", encoding="utf-8")
    for index, line in enumerate(_file.read().splitlines()):
        if line.endswith("fields=["):
            fields = True
        if line.endswith('"created_at",'):
            moved = True
            moved_section.append(new_file[-1])
            del new_file[-1]

        if count >= 7:
            moved = False
            count = 0

        if line == "            ],":
            assert not moved
            assert not count
            new_file += moved_section
            moved_section = []
            fields = False

        if moved:
            moved_section.append(line)
            count += 1
        else:
            new_file.append(line)

    _file.close()
    with open(filename, "w") as f:
        for line in new_file:
            f.write(f"{line}\n")


fix_file()
