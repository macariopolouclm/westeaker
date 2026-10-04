from qiskit_aer import AerSimulator

from qiskit_ibm_runtime.fake_provider import (
    FakeAlmadenV2,
    FakeMelbourneV2,
    FakeMarrakesh,
    FakeFez,
    #FakeKingston
)


BACKEND_CLASSES = [
    AerSimulator,
    FakeAlmadenV2,
    FakeMelbourneV2,
    FakeMarrakesh,
    FakeFez,
    #FakeKingston
]


BACKEND_FACTORIES = {
    backend_class().name: backend_class
    for backend_class in BACKEND_CLASSES
}


DEFAULT_BACKENDS = [
    #AerSimulator().name,
    FakeMarrakesh().name,
]


def create_backends(names: list[str] | None) -> list:

    if not names:
        names = DEFAULT_BACKENDS

    unknown = [
        name
        for name in names
        if name not in BACKEND_FACTORIES
    ]

    if unknown:
        raise ValueError(
            f"Unknown backends: {', '.join(unknown)}"
        )

    return [
        BACKEND_FACTORIES[name]()
        for name in names
    ]