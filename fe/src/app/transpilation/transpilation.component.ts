import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackendSelectorComponent } from '../backend-selector/backend-selector.component';
import { BackendInfo } from '../models/BackendInfo';
import { GenerationService } from '../generation-service.service';
import { TranspilationService } from '../transpilation.service';
import { FailedBackend } from '../models/FailedBackend';
import { TranspilationRequest } from '../models/Transpilation';

@Component({
  selector: 'app-transpilation',
  standalone: true,
  imports: [FormsModule, BackendSelectorComponent],
  templateUrl: './transpilation.component.html',
  styleUrl: './transpilation.component.css'
})
export class TranspilationComponent implements OnInit {
  code = `from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from math import pi

qubits = 4
outputQubits = 4
ORIGINAL_QUBITS = 4

SPLIT = False

shots = 1024


expected = [(0, 0.019337016574585635),(1, 0.08425414364640885),(2, 0.012430939226519336),(3, 0.11049723756906077),(4, 0.06353591160220995),(5, 0.055248618784530384),(6, 0.0718232044198895),(7, 0.049723756906077346),(8, 0.106353591160221),(9, 0.023480662983425413),(10, 0.12430939226519337),
(11, 0.09116022099447514),(12, 0.06353591160220995),(13, 0.0787292817679558),(14, 0.015193370165745856),(15, 0.03038674033149171),]
	
qc = QuantumCircuit(qubits, qubits)
ALGORITHM = "Greenoble"
	  
ONE = [0, 1]
ZERO = [1, 0]

def get2RL_0() :
	U = QuantumCircuit(1, name="2RL_0")
	U.ry(0.2506152391433716, 0)
	return U.to_gate()

def get2LL_0() :
	U = QuantumCircuit(1, name="2LL_0")
	U.ry(0.08546985685825348, 0)
	return U.to_gate()

def get2RR_0() :
	U = QuantumCircuit(1, name="2RR_0")
	U.ry(-0.540664553642273, 0)
	return U.to_gate()

def get2LR_0() :
	U = QuantumCircuit(1, name="2LR_0")
	U.ry(0.011494532227516174, 0)
	return U.to_gate()

def get1R_0() :
	U = QuantumCircuit(1, name="1R_0")
	U.ry(-0.2998080551624298, 0)
	return U.to_gate()

def get3RLL() :
	U = QuantumCircuit(1, name="3RLL")
	U.ry(-0.6922851204872131, 0)
	return U.to_gate()

def get3RLR() :
	U = QuantumCircuit(1, name="3RLR")
	U.ry(-0.15445959568023682, 0)
	return U.to_gate()

def get3LLL() :
	U = QuantumCircuit(1, name="3LLL")
	U.ry(0.677268385887146, 0)
	return U.to_gate()

def get3LLR() :
	U = QuantumCircuit(1, name="3LLR")
	U.ry(0.9235591888427734, 0)
	return U.to_gate()

def get3RRL() :
	U = QuantumCircuit(1, name="3RRL")
	U.ry(0.1070002019405365, 0)
	return U.to_gate()

def get3RRR() :
	U = QuantumCircuit(1, name="3RRR")
	U.ry(0.33983689546585083, 0)
	return U.to_gate()

def get3LRL() :
	U = QuantumCircuit(1, name="3LRL")
	U.ry(-0.06982419639825821, 0)
	return U.to_gate()

def get3LRR() :
	U = QuantumCircuit(1, name="3LRR")
	U.ry(-0.18283508718013763, 0)
	return U.to_gate()

def get1L_0() :
	U = QuantumCircuit(1, name="1L_0")
	U.ry(0.029590096324682236, 0)
	return U.to_gate()

def get0_0() :
	U = QuantumCircuit(1, name="0_0")
	U.ry(0.06634703278541565, 0)
	return U.to_gate()

def get2RL() :
	U = QuantumCircuit(2, name="2RL")
	U.append(get2RL_0(), range(0, 1))
	U.x(0)
	U.append(get3RLL().control(1), [0, 1])
	U.x(0)
	U.append(get3RLR().control(1), [0, 1])
	return U.to_gate()

def get2LL() :
	U = QuantumCircuit(2, name="2LL")
	U.append(get2LL_0(), range(0, 1))
	U.x(0)
	U.append(get3LLL().control(1), [0, 1])
	U.x(0)
	U.append(get3LLR().control(1), [0, 1])
	return U.to_gate()

def get2RR() :
	U = QuantumCircuit(2, name="2RR")
	U.append(get2RR_0(), range(0, 1))
	U.x(0)
	U.append(get3RRL().control(1), [0, 1])
	U.x(0)
	U.append(get3RRR().control(1), [0, 1])
	return U.to_gate()

def get2LR() :
	U = QuantumCircuit(2, name="2LR")
	U.append(get2LR_0(), range(0, 1))
	U.x(0)
	U.append(get3LRL().control(1), [0, 1])
	U.x(0)
	U.append(get3LRR().control(1), [0, 1])
	return U.to_gate()

def get1R() :
	U = QuantumCircuit(3, name="1R")
	U.append(get1R_0(), range(0, 1))
	U.x(0)
	U.append(get2RL().control(1), [0, 1, 2])
	U.x(0)
	U.append(get2RR().control(1), [0, 1, 2])
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

for j in range(startQubit, qubits) :
	qc.h(j)
qc.append(get0(), [0,1,2,3])

for j in range(startQubit, qubits) :
	qc.measure(j, qubits-j-1)

#expanded = circuits[0].decompose(reps=2)   # Esto es para pintar el circuit. A mayor reps, más detalla.
#print(expanded)
`;
  availableBackends: BackendInfo[] = [];
  selectedBackends: BackendInfo[] = [];
  failedBackends: FailedBackend[] = [];
  results: any[] = [];
  loading = false;
  error = '';
  filename = 'circuit.py';

  constructor(private generationService: GenerationService, private transpilationService: TranspilationService) {}

  ngOnInit(): void {
    this.generationService.getBackends().subscribe({
      next: backends => this.availableBackends = backends,
      error: error => console.error(error)
    });
  }

  transpile(): void {
  if (!this.filename.trim() || !this.code.trim() || this.selectedBackends.length === 0) return;
  const request: TranspilationRequest = {
    filename: this.filename,
    code: this.code,
    backends: this.selectedBackends
  };
  this.loading = true;
  this.error = '';
  this.failedBackends = [];
  this.results = [];
  this.transpilationService.transpile(request).subscribe({
    next: response => {
      this.results = response.results ?? [];
      this.failedBackends = response.failed_backends ?? [];
      this.loading = false;
    },
    error: error => {
      this.error = error.error?.detail ?? error.message ?? 'Error transpiling circuit.';
      this.loading = false;
    }
  });
}
}