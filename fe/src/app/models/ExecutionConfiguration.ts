export interface ExecutionConfiguration {
  backend: string;
  filename: string;
  origin: 'composed_grovers' | 'whole_grovers';
  transpiled_first: string;
  qubits: number;
  searched_values: number[];
}