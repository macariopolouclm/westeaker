import importlib
from pathlib import Path
import sys

from qiskit import QuantumCircuit

def _load_module(python_filename) :
    if not python_filename.exists():
        raise FileNotFoundError(f"File not found: {python_filename}")
    
    file_path = Path(python_filename)
    module_name = file_path.stem
    module_dir = str(file_path.parent)
    sys.path.insert(0, module_dir)
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(module_dir)

import importlib
import importlib.util
import sys
from pathlib import Path


def load_module(filename):
    file_path = Path(filename).resolve()

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    module_dir = str(file_path.parent)

    local_module_names = {
        path.stem
        for path in file_path.parent.glob("*.py")
    }

    previous_modules = {
        name: sys.modules.get(name)
        for name in local_module_names
    }

    for name in local_module_names:
        sys.modules.pop(name, None)

    sys.path.insert(0, module_dir)
    importlib.invalidate_caches()

    try:
        module_name = file_path.stem

        spec = importlib.util.spec_from_file_location(module_name, file_path)

        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module: {file_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module

    finally:
        sys.path.remove(module_dir)

        # Quitamos los módulos locales que acabamos de cargar
        for name in local_module_names:
            sys.modules.pop(name, None)

        # Restauramos los que pudieran existir anteriormente
        for name, previous_module in previous_modules.items():
            if previous_module is not None:
                sys.modules[name] = previous_module

def generate_subcircuit(circuit: QuantumCircuit, function_name: str | None, initial_layout=None, cl_bits=None) -> str:
    indent = "    " if function_name is not None else ""

    if function_name is None:
        lines = [
            "from qiskit import QuantumCircuit\n\n",
            f"qc = QuantumCircuit({circuit.num_qubits}, {cl_bits})",
        ]
    else:
        function_signature = f"def {function_name}(initial_layout: list[int] | None = None) -> QuantumCircuit :"

        lines = [
            "from qiskit import QuantumCircuit\n\n",
            function_signature,
            f"    qc = QuantumCircuit({circuit.num_qubits}, {circuit.num_clbits}, name='{function_name}')",
        ]

    physical_to_logical = {}

    if initial_layout is not None:
        physical_to_logical = {
            physical: logical
            for logical, physical in enumerate(initial_layout)
        }

    def qubit_ref(index: int) -> str:
        if index in physical_to_logical:
            return f"initial_layout[{physical_to_logical[index]}]"
        return str(index)

    def qubit_list(indices: list[int]) -> str:
        return "[" + ", ".join(qubit_ref(index) for index in indices) + "]"

    for instruction, qargs, cargs in circuit.data:
        name = instruction.name

        q_indices = [circuit.find_bit(q).index for q in qargs]
        c_indices = [circuit.find_bit(c).index for c in cargs]

        if name == "h":
            lines.append(f"{indent}qc.h({qubit_ref(q_indices[0])})")
        elif name == "x":
            lines.append(f"{indent}qc.x({qubit_ref(q_indices[0])})")
        elif name == "y":
            lines.append(f"{indent}qc.y({qubit_ref(q_indices[0])})")
        elif name == "z":
            lines.append(f"{indent}qc.z({qubit_ref(q_indices[0])})")
        elif name == "s":
            lines.append(f"{indent}qc.s({qubit_ref(q_indices[0])})")
        elif name == "sdg":
            lines.append(f"{indent}qc.sdg({qubit_ref(q_indices[0])})")
        elif name == "t":
            lines.append(f"{indent}qc.t({qubit_ref(q_indices[0])})")
        elif name == "tdg":
            lines.append(f"{indent}qc.tdg({qubit_ref(q_indices[0])})")
        elif name == "sx":
            lines.append(f"{indent}qc.sx({qubit_ref(q_indices[0])})")
        elif name == "sxdg":
            lines.append(f"{indent}qc.sxdg({qubit_ref(q_indices[0])})")
        elif name == "p":
            theta = repr(float(instruction.params[0]))
            lines.append(f"{indent}qc.p({theta}, {qubit_ref(q_indices[0])})")
        elif name == "rx":
            theta = repr(float(instruction.params[0]))
            lines.append(f"{indent}qc.rx({theta}, {qubit_ref(q_indices[0])})")
        elif name == "ry":
            theta = repr(float(instruction.params[0]))
            lines.append(f"{indent}qc.ry({theta}, {qubit_ref(q_indices[0])})")
        elif name == "rz":
            theta = repr(float(instruction.params[0]))
            lines.append(f"{indent}qc.rz({theta}, {qubit_ref(q_indices[0])})")
        elif name == "u":
            theta = repr(float(instruction.params[0]))
            phi = repr(float(instruction.params[1]))
            lam = repr(float(instruction.params[2]))
            lines.append(f"{indent}qc.u({theta}, {phi}, {lam}, {qubit_ref(q_indices[0])})")
        elif name == "u1":
            lam = repr(float(instruction.params[0]))
            lines.append(f"{indent}qc.u(0.0, 0.0, {lam}, {qubit_ref(q_indices[0])})")
        elif name == "u2":
            phi = repr(float(instruction.params[0]))
            lam = repr(float(instruction.params[1]))
            lines.append(f"{indent}qc.u(1.5707963267948966, {phi}, {lam}, {qubit_ref(q_indices[0])})")
        elif name == "u3":
            theta = repr(float(instruction.params[0]))
            phi = repr(float(instruction.params[1]))
            lam = repr(float(instruction.params[2]))
            lines.append(f"{indent}qc.u({theta}, {phi}, {lam}, {qubit_ref(q_indices[0])})")
        elif name == "cx":
            lines.append(f"{indent}qc.cx({qubit_ref(q_indices[0])}, {qubit_ref(q_indices[1])})")
        elif name == "cz":
            lines.append(f"{indent}qc.cz({qubit_ref(q_indices[0])}, {qubit_ref(q_indices[1])})")
        elif name == "swap":
            lines.append(f"{indent}qc.swap({qubit_ref(q_indices[0])}, {qubit_ref(q_indices[1])})")
        elif name == "cp":
            theta = repr(float(instruction.params[0]))
            lines.append(f"{indent}qc.cp({theta}, {qubit_ref(q_indices[0])}, {qubit_ref(q_indices[1])})"            )
        elif name in ("mcp", "mcphase"):
            theta = repr(float(instruction.params[0]))
            controls = q_indices[:-1]
            target = q_indices[-1]
            lines.append(f"{indent}qc.mcp({theta}, {qubit_list(controls)}, {qubit_ref(target)})")
        elif name == "ccx":
            lines.append(
                f"{indent}qc.ccx({qubit_ref(q_indices[0])}, "
                f"{qubit_ref(q_indices[1])}, "
                f"{qubit_ref(q_indices[2])})"
            )
        elif name == "mcx":
            controls = q_indices[:-1]
            target = q_indices[-1]
            lines.append(f"{indent}qc.mcx({qubit_list(controls)}, {qubit_ref(target)})")
        elif name == "cswap":
            lines.append(f"{indent}qc.cswap({qubit_ref(q_indices[0])}, "
                f"{qubit_ref(q_indices[1])}, "
                f"{qubit_ref(q_indices[2])})"
            )
        elif name == "ecr":
            lines.append(f"{indent}qc.ecr({qubit_ref(q_indices[0])}, {qubit_ref(q_indices[1])})")
        elif name == "measure":
            lines.append(f"{indent}qc.measure({qubit_ref(q_indices[0])}, {c_indices[0]})")
        elif name == "reset":
            lines.append(f"{indent}qc.reset({qubit_ref(q_indices[0])})")
        elif name == "delay":
            duration = repr(instruction.params[0])

            if getattr(instruction, "unit", None):
                lines.append(
                    f"{indent}qc.delay({duration}, {qubit_ref(q_indices[0])}, "
                    f"unit={instruction.unit!r})"
                )
            else:
                lines.append(
                    f"{indent}qc.delay({duration}, {qubit_ref(q_indices[0])})"
                )

        elif name == "initialize":
            value = instruction.params[0]
            lines.append(f"{indent}qc.initialize({value}, {qubit_ref(q_indices[0])})")
        elif name == "crz":
            value = instruction.params[0]
            lines.append(
                f"{indent}qc.crz({value}, "
                f"{qubit_ref(q_indices[0])}, "
                f"{qubit_ref(q_indices[1])})"
            )
        else:
            lines.append(f"{indent}qc.{name}({qubit_list(q_indices)})")

    if function_name is not None :
        lines.append("    return qc")
    return "\n".join(lines)

def get_function_name(clbits : int, searched_values : list[int]) -> str :
    return "get_qc" + f"_{clbits}_{'_'.join(map(str, searched_values))}"

