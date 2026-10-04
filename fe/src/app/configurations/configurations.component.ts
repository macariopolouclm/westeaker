import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ExecutionService } from '../execution.service';
import { ExecuteFileRequest } from '../models/ExecutionFileRequest';
import { ExecutionConfiguration } from '../models/ExecutionConfiguration';
import { concatMap, finalize, from } from 'rxjs';


type SortColumn =
  | 'backend'
  | 'filename'
  | 'qubits'
  | 'transpiled_first'
  | 'searched_values';


@Component({
  selector: 'app-configurations',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './configurations.component.html',
  styleUrl: './configurations.component.css'
})
export class ConfigurationsComponent implements OnInit {

  configurations: ExecutionConfiguration[] = [];
  selectedConfigurations = new Set<string>();
  executingSelected = false;

  loading = false;
  error = '';

  backendFilter = '';
  filenameFilter = '';
  qubitsFilter = '';
  transpiledFirstFilter = '';
  searchedValuesFilter = '';

  sortColumn: SortColumn | null = null;
  sortAscending = true;

  executingConfiguration = '';

  shots = 1024;

  selectedFilename = '';
  selectedSource = '';
  sourceLoading = false;
  sourceError = '';
  showSourceModal = false;

  constructor(private executionService: ExecutionService) { }


  ngOnInit(): void {
    this.loadConfigurations();
  }


  loadConfigurations(): void {
    this.loading = true;
    this.error = '';

    this.executionService.getConfigurations().subscribe({
      next: configurations => {
        this.configurations = configurations;
        this.loading = false;
      },

      error: error => {
        this.error =
          error.error?.detail ??
          error.message ??
          'Error loading configurations.';

        this.loading = false;
      }
    });
  }


  get backendValues(): string[] {
    return [...new Set(
      this.configurations.map(configuration => configuration.backend)
    )].sort();
  }


  get filenameValues(): string[] {
    return [...new Set(
      this.configurations.map(configuration => configuration.filename)
    )].sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  }


  get qubitsValues(): number[] {
    return [...new Set(
      this.configurations.map(configuration => configuration.qubits)
    )].sort((a, b) => a - b);
  }


  get transpiledFirstValues(): string[] {
    return [...new Set(
      this.configurations.map(configuration => configuration.transpiled_first)
    )].sort();
  }


  get searchedValues(): string[] {
    return [...new Set(
      this.configurations.map(
        configuration => configuration.searched_values.join(',')
      )
    )].sort((a, b) =>
      a.localeCompare(b, undefined, { numeric: true })
    );
  }


  get filteredConfigurations(): ExecutionConfiguration[] {
    const configurations = this.configurations.filter(configuration =>
      (!this.backendFilter ||
        configuration.backend === this.backendFilter) &&

      (!this.filenameFilter ||
        configuration.filename === this.filenameFilter) &&

      (!this.qubitsFilter ||
        configuration.qubits === Number(this.qubitsFilter)) &&

      (!this.transpiledFirstFilter ||
        configuration.transpiled_first === this.transpiledFirstFilter) &&

      (!this.searchedValuesFilter ||
        configuration.searched_values.join(',') === this.searchedValuesFilter)
    );

    if (!this.sortColumn) {
      return configurations;
    }

    return [...configurations].sort((a, b) => {
      let comparison = 0;

      switch (this.sortColumn) {

        case 'backend':
          comparison = a.backend.localeCompare(b.backend);
          break;

        case 'filename':
          comparison = a.filename.localeCompare(
            b.filename,
            undefined,
            { numeric: true }
          );
          break;

        case 'qubits':
          comparison = a.qubits - b.qubits;
          break;

        case 'transpiled_first':
          comparison = a.transpiled_first.localeCompare(
            b.transpiled_first
          );
          break;

        case 'searched_values':
          comparison = a.searched_values.join(',').localeCompare(
            b.searched_values.join(','),
            undefined,
            { numeric: true }
          );
          break;
      }

      return this.sortAscending ? comparison : -comparison;
    });
  }


  sortConfigurations(column: SortColumn): void {
    if (this.sortColumn === column) {
      this.sortAscending = !this.sortAscending;
    } else {
      this.sortColumn = column;
      this.sortAscending = true;
    }
  }


  getSortIndicator(column: SortColumn): string {
    if (this.sortColumn !== column) {
      return '';
    }

    return this.sortAscending ? '▲' : '▼';
  }


  clearFilters(): void {
    this.backendFilter = '';
    this.filenameFilter = '';
    this.qubitsFilter = '';
    this.transpiledFirstFilter = '';
    this.searchedValuesFilter = '';
  }


  execute(configuration: ExecutionConfiguration): void {
    const key = this.getConfigurationKey(configuration);

    const request: ExecuteFileRequest = {
      backend: configuration.backend,
      filename: configuration.filename,
      origin: configuration.origin,
      searched_values: configuration.searched_values,
      shots: this.shots
    };

    this.executingConfiguration = key;
    this.error = '';

    this.executionService.executeFile(request).subscribe({
      next: result => {
        console.log('Execution result:', result);
        this.executingConfiguration = '';
      },

      error: error => {
        this.error =
          error.error?.detail ??
          error.message ??
          'Error executing configuration.';

        this.executingConfiguration = '';
      }
    });
  }


  isExecuting(configuration: ExecutionConfiguration): boolean {
    return this.executingConfiguration ===
      this.getConfigurationKey(configuration);
  }


  private getConfigurationKey(
    configuration: ExecutionConfiguration
  ): string {
    return `${configuration.origin}/${configuration.backend}/${configuration.filename}`;
  }

  showSource(configuration: ExecutionConfiguration): void {
    this.selectedFilename = configuration.filename;
    this.selectedSource = '';
    this.sourceError = '';
    this.sourceLoading = true;
    this.showSourceModal = true;
    this.executionService.getSource(configuration).subscribe({
      next: source => {
        this.selectedSource = source;
        this.sourceLoading = false;
      },
      error: error => {
        this.sourceError = error.error?.detail ?? error.message ?? 'Error loading source code.';
        this.sourceLoading = false;
      }
    });
  }

  closeSource(): void {
    this.showSourceModal = false;
  }

  isSelected(configuration: ExecutionConfiguration): boolean {
    return this.selectedConfigurations.has(this.getConfigurationKey(configuration));
  }
  toggleSelection(configuration: ExecutionConfiguration, selected: boolean): void {
    const key = this.getConfigurationKey(configuration);
    if (selected) {
      this.selectedConfigurations.add(key);
    } else {
      this.selectedConfigurations.delete(key);
    }
  }
  get selectedCount(): number {
    return this.selectedConfigurations.size;
  }
  executeSelected(): void {
    const selected = this.configurations.filter(configuration =>
      this.selectedConfigurations.has(this.getConfigurationKey(configuration))
    );
    if (selected.length === 0) return;
    this.executingSelected = true;
    this.error = '';
    from(selected).pipe(
      concatMap(configuration => {
        const request: ExecuteFileRequest = {
          backend: configuration.backend,
          filename: configuration.filename,
          origin: configuration.origin,
          searched_values: configuration.searched_values,
          shots: this.shots
        };
        this.executingConfiguration = this.getConfigurationKey(configuration);
        return this.executionService.executeFile(request);
      }),
      finalize(() => {
        this.executingConfiguration = '';
        this.executingSelected = false;
      })
    ).subscribe({
      next: result => {
        console.log('Execution result:', result);
      },
      error: error => {
        this.error = error.error?.detail ?? error.message ?? 'Error executing configurations.';
      }
    });
  }

  clearSelection(): void {
    this.selectedConfigurations.clear();
  }

  get allFilteredSelected(): boolean {
    return this.filteredConfigurations.length > 0 &&
      this.filteredConfigurations.every(configuration => this.isSelected(configuration));
  }
  get someFilteredSelected(): boolean {
    return this.filteredConfigurations.some(configuration => this.isSelected(configuration)) &&
      !this.allFilteredSelected;
  }
  toggleSelectAll(selected: boolean): void {
    for (const configuration of this.filteredConfigurations) {
      const key = this.getConfigurationKey(configuration);
      if (selected) {
        this.selectedConfigurations.add(key);
      } else {
        this.selectedConfigurations.delete(key);
      }
    }
  }
}