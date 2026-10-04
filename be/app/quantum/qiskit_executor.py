import time

def run(backend, qc, current_shots):
    run_time = time.time()
    job = backend.run(qc, shots=current_shots)
    result = job.result()
    counts = result.get_counts()
    run_time = time.time() - run_time
    counts = dict(sorted(counts.items()))
    return counts, run_time