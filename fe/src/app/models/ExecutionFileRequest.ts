export interface ExecuteFileRequest {
  backend: string;
  filename: string;
  origin: 'composed_grovers' | 'whole_grovers';
  searched_values: number[];
  shots: number;
}