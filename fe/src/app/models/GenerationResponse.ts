import { FailedBackend } from "./FailedBackend";

export interface GenerationResponse {
  generated_files: string[];
  found_files: string[];
  failed_backends: FailedBackend[];
}