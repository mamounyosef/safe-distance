"""List the files inside a zip on the web without downloading it (reads only the zip's index).

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe scripts\\list_remote_zip.py <url> [how many names to show]
"""

import sys
from collections import Counter

from remotezip import RemoteZip


def main() -> None:
    url = sys.argv[1]
    show = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    with RemoteZip(url) as z:
        infos = [i for i in z.infolist() if not i.is_dir()]
    sizes = [i.file_size for i in infos]
    print(f"{len(infos)} files, {sum(sizes) / 1e9:.2f} GB unpacked")
    print("extensions:", Counter(i.filename.rsplit('.', 1)[-1].lower() for i in infos).most_common(5))
    if sizes:
        s = sorted(sizes)
        print(f"file size MB: min {s[0] / 1e6:.1f}, median {s[len(s) // 2] / 1e6:.1f}, max {s[-1] / 1e6:.1f}")
    for i in infos[:show]:
        print(f"  {i.file_size / 1e6:7.1f} MB  {i.filename}")


if __name__ == "__main__":
    main()
