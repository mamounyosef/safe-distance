"""Download openpilot's driving model (ONNX) and print its inputs and outputs.

The file sits in Git LFS (large file storage) in the openpilot repo; GitHub
serves the real file at media.githubusercontent.com. The model stores the
meaning of its single output vector (which numbers are the lead car, the hard
brake probabilities, ...) as a pickled dict of slices in its metadata.

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe scripts\\inspect_openpilot_model.py
"""

import base64
import pickle
from pathlib import Path
from urllib.request import urlretrieve

import numpy as np
import onnx

# ---- CONFIG ----
URL = ("https://media.githubusercontent.com/media/commaai/openpilot/master/"
       "openpilot/selfdrive/modeld/models/driving_supercombo.onnx")
DEST = Path(r"C:\safe-distance-data\models\openpilot\driving_supercombo.onnx")
# ----------------


def main() -> None:
    if not DEST.exists():
        DEST.parent.mkdir(parents=True, exist_ok=True)
        print(f"downloading {URL}")
        urlretrieve(URL, DEST)
    print(f"{DEST}: {DEST.stat().st_size / 1e6:.1f} MB")
    model = onnx.load(str(DEST))
    shape = lambda v: [d.dim_value or d.dim_param for d in v.type.tensor_type.shape.dim]  # noqa: E731
    elem = lambda v: onnx.TensorProto.DataType.Name(v.type.tensor_type.elem_type)  # noqa: E731
    print("INPUTS")
    for v in model.graph.input:
        print(f"  {v.name}: {elem(v)} {shape(v)}")
    print("OUTPUTS")
    for v in model.graph.output:
        print(f"  {v.name}: {elem(v)} {shape(v)}")
    print("METADATA")
    for p in model.metadata_props:
        if p.key == "output_slices":
            # Only a dict of builtin slice objects; safe to unpickle from this known source.
            slices = pickle.loads(base64.b64decode(p.value))
            total = shape(model.graph.output[0])[-1]
            for name, s in slices.items():
                start, stop, _ = s.indices(total)     # resolves None and negative ends
                print(f"  output[{start}:{stop}] ({stop - start} numbers): {name}")
        else:
            print(f"  {p.key}: {p.value[:200]}")
    params = sum(int(np.prod(t.dims)) for t in model.graph.initializer)
    print(f"parameters: {params / 1e6:.1f} M")


if __name__ == "__main__":
    main()
