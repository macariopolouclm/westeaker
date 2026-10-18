import { BackendInfo } from "./BackendInfo";
import { FailedBackend } from "./FailedBackend";

export interface GroverRequest {
  qubits: number[];
  markable_values: number[];
  backends: BackendInfo[] | null;
  searched_values?: number[][];
  default_values: boolean;
  repetitions: number;
}

export interface SavedGroverRequest extends GroverRequest {
  failed_backends?: FailedBackend[];
}