import os
from qiskit_ionq import IonQProvider
import sys
from qiskit import transpile

print(sys.executable)
print(sys.path)
# Load your API key from an environment variable named MY_IONQ_API_KEY
my_api_key = "EMoB4RJmrKBzN5Gg3uHXi5ZVdYFjXhEx"
provider = IonQProvider(my_api_key)

print(provider.backends())
for backend in provider.backends():
    print(backend.name)

simulator_backend = provider.get_backend("simulator")


from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from math import pi

qubits = 4
outputQubits = 4
ORIGINAL_QUBITS = 4

SPLIT = False

shots = 1024


expected = [(0, 0.25),(2, 0.25),(5, 0.25),(13, 0.25),]
	
circuits = [QuantumCircuit(qubits, qubits)]
ALGORITHM = "Greenoble"
	  
ONE = [0, 1]
ZERO = [1, 0]

def get1R_0() :
	U = QuantumCircuit(1, name="1R_0")
	U.ry(1.5707963705062866, 0)
	return U.to_gate()

def get3LLL() :
	U = QuantumCircuit(1, name="3LLL")
	U.ry(-1.5707963705062866, 0)
	return U.to_gate()

def get1L_0() :
	U = QuantumCircuit(1, name="1L_0")
	U.ry(-0.3398369550704956, 0)
	return U.to_gate()

def get0_0() :
	U = QuantumCircuit(1, name="0_0")
	U.ry(-0.5235987901687622, 0)
	return U.to_gate()

def get2LL() :
	U = QuantumCircuit(2, name="2LL")
	U.x(0)
	U.append(get3LLL().control(1), [0, 1])
	U.x(0)
	U.append(get3LLL().control(1), [0, 1])
	return U.to_gate()

def get2RR() :
	U = QuantumCircuit(2, name="2RR")
	U.append(get3LLL(), range(0, 1))
	U.append(get1R_0(), range(1, 2))
	return U.to_gate()

def get2LR() :
	U = QuantumCircuit(2, name="2LR")
	U.append(get3LLL(), range(0, 1))
	U.append(get1R_0(), range(1, 2))
	return U.to_gate()

def get1R() :
	U = QuantumCircuit(3, name="1R")
	U.append(get1R_0(), range(0, 1))
	U.append(get2RR(), range(1, 3))
	return U.to_gate()

def get1L() :
	U = QuantumCircuit(3, name="1L")
	U.append(get1L_0(), range(0, 1))
	U.x(0)
	U.append(get2LL().control(1), [0, 1, 2])
	U.x(0)
	U.append(get2LR().control(1), [0, 1, 2])
	return U.to_gate()

def get0() :
	U = QuantumCircuit(4, name="0")
	U.append(get0_0(), range(0, 1))
	U.x(0)
	U.append(get1L().control(1), [0, 1, 2, 3])
	U.x(0)
	U.append(get1R().control(1), [0, 1, 2, 3])
	return U.to_gate()





startQubit = qubits-outputQubits

########### OJO: dependiendo del problema, es posible que necesites que los cúbits se pongan en superposición al principio.
########### Si lo necesitas y el algoritmo no lo ha hecho, descomenta las líneas siguientes. ¡Feliz ejecución 🤪!

'''
for i in range(0, len(circuits)) :
	for j in range(startQubit, qubits) :
		circuits[i].h(j)
'''

for i in range(0, len(circuits)) :
	for j in range(startQubit, qubits) :
		circuits[i].h(j)
	circuits[i].append(get0(), [0,1,2,3])

for i in range(0, len(circuits)) :
	for j in range(startQubit, qubits) :
		circuits[i].measure(j, qubits-j-1)

#expanded = circuits[0].decompose(reps=2)   # Esto es para pintar el circuit. A mayor reps, más detalla.
#print(expanded)

qc = circuits[0]
qc = transpile(qc, backend=simulator_backend, optimization_level=0)
#print(qc)

job = simulator_backend.run(qc, shots=10000)
print(job.get_counts())