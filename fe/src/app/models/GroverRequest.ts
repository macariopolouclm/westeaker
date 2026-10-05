export interface GroverRequest {
  qubits: number[];
  markable_values: number[];
  backends: string[] | null;
  searched_values?: number[][];
  default_values: boolean;
  repetitions: number;
}