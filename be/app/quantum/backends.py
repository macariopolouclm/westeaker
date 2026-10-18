import os
from app.quantum.BackendWrapper import BackendWrapper
from qiskit_aer import AerSimulator
from qiskit_ionq import IonQProvider
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime.fake_provider import FakeProviderForBackendV2

BACKENDS : dict[str, BackendWrapper] = {}
BACKEND_NOISE_MODELS = {}
IONQ_NOISE_MODELS = ["ideal", "aria-1", "forte-1"]

DEFAULT_BACKEND = "fake_marrakesh"
_BACKENDS_INITIALIZED = False

ibmKey = "f36be7dffb684988a853d020195b1761"
ionQKey = "EMoB4RJmrKBzN5Gg3uHXi5ZVdYFjXhEx"

def _register_backend(backend, provider: str, noise_model: list[str] | None = None):
    wrapper = BackendWrapper(backend=backend, provider=provider, noise_model=noise_model)
    BACKENDS[wrapper.name] = wrapper

def initialize_backends():
    global _BACKENDS_INITIALIZED
    if _BACKENDS_INITIALIZED:
        return
    BACKENDS.clear()
    _load_local_backends()
    _load_ibm_backends()
    _load_ionq_backends()
    print(f"{len(BACKENDS)} backends available")
    for backend in BACKENDS.values():
        print(f"{backend.name} ({backend.provider}, {backend.num_qubits} qubits)")
    _BACKENDS_INITIALIZED = True

def _load_local_backends():
    aer = AerSimulator()
    _register_backend(aer, "local")
    fake_provider = FakeProviderForBackendV2()
    for backend in fake_provider.backends():
        _register_backend(backend, "local")

def _load_ibm_backends():
    try:
        service = QiskitRuntimeService(
            channel="ibm_quantum_platform",
            token=ibmKey
        )
        for backend in service.backends():
            _register_backend(backend, "ibm")
    except Exception as exception:
        print(f"IBM backends unavailable: {exception}")

def _load_ionq_backends():
    try:
        if not ionQKey:
            print("IonQ backends unavailable: IONQ_API_KEY is not defined")
            return
        provider = IonQProvider(ionQKey)
        for backend in provider.backends():
            if backend.name == "ionq_simulator":
                for noise_model in IONQ_NOISE_MODELS:
                    current_backend = provider.get_backend(backend.name, gateset="native")
                    _register_backend(current_backend, "ionq", noise_model)
            else:
                _register_backend(backend, "ionq")
    except Exception as exception:
        print(f"IonQ backends unavailable: {exception}")

def get_available_backends() -> list[dict]:
    result = []
    for backend in BACKENDS.values():
        result.append({
            "name": backend.name,
            "num_qubits": backend.num_qubits
        })
    return result

def find_backend(backend_name) -> BackendWrapper:
    return BACKENDS[backend_name]

def get_backend(backend_info) -> BackendWrapper:
    return BACKENDS[backend_info.name]

def get_backends(backend_infos: str | list | None) -> list[BackendWrapper]:
    if not backend_infos:
        return [BACKENDS[DEFAULT_BACKEND]]
    if isinstance(backend_infos, str):
        backend_infos = [backend_infos]
    return [get_backend(backend_info) for backend_info in backend_infos]