import { BackendInfo } from "./BackendInfo";
import { FailedBackend } from "./FailedBackend";

export interface TranspilationRequest {
  filename: string;
  code: string;
  backends: BackendInfo[];
}

export interface TranspilationResult {
  backend: string;
  code: string;
}

export interface TranspilationResponse {
  results: TranspilationResult[];
  failed_backends: FailedBackend[];
}