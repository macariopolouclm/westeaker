import { Component, ElementRef, OnInit, QueryList, ViewChildren } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { JsonPipe } from '@angular/common';
import { GenerationService } from '../generation-service.service';
import { GroverRequest, SavedGroverRequest } from '../models/GroverRequest';
import { BackendInfo } from '../models/BackendInfo';
import { FailedBackend } from '../models/FailedBackend';


@Component({
  selector: 'app-generation',
  standalone: true,
  imports: [FormsModule, JsonPipe],
  templateUrl: './generation.component.html',
  styleUrl: './generation.component.css'
})
export class GenerationComponent implements OnInit {

  @ViewChildren('searchedInput') searchedInputs!: QueryList<ElementRef<HTMLInputElement>>;

  qubits = '4, 5, 6';
  availableBackends: BackendInfo[] = [];

  markableValues = '1, 2, 3, 4, 5';
  searchedValuesInputs: string[] = [''];
  defaultValues = false;

  repetitions = 1;

  selectedBackends: BackendInfo[] = [];

  loading = false;
  error = '';
  result: any = null;

  resultsRows: string[][] = [];
  resultsHeader: string[] = [];
  resultsLoading = false;
  resultsError = '';
  failedBackends: FailedBackend[] = [];

  constructor(private generationService: GenerationService) { }

  ngOnInit(): void {
    this.getBackends()

    const savedRequest = localStorage.getItem('generationRequest');
    if (savedRequest) {
      const request: SavedGroverRequest = JSON.parse(savedRequest);
      this.qubits = request.qubits.join(', ');
      this.markableValues = request.markable_values.join(', ');
      this.selectedBackends = request.backends ?? [];
      const searchedValues = request.searched_values?.map(values => values.join(', ')) ?? [];
      this.searchedValuesInputs = searchedValues.length > 0 ? searchedValues : [''];
      //this.searchedValuesInputs = request.searched_values?.map(values => values.join(', ')) ?? [''];
      this.defaultValues = request.default_values;
      this.repetitions = request.repetitions ?? 10;
      this.failedBackends = request.failed_backends ?? [];
    }
  }

  getBackends() {
    this.generationService.getBackends().subscribe(
      backends => {
        this.availableBackends = backends
      },
      error => {
        console.error(error)
      }
    );
  }

  generate(): void {
    this.error = '';
    this.failedBackends = [];
    this.result = null;

    const qubits = this.parseValues(this.qubits);
    const markableValues = this.parseValues(this.markableValues);

    if (qubits.length <= 0) {
      this.error = 'Qubits must be greater than 0.';
      return;
    }

    if (markableValues.length === 0) {
      this.error = 'At least one markable value is required.';
      return;
    }

    if (this.selectedBackends.length === 0) {
      this.error = 'At least one backend must be selected.';
      return;
    }

    const request: GroverRequest = {
      qubits: this.parseValues(this.qubits),
      markable_values: this.parseValues(this.markableValues),
      backends: this.selectedBackends,
      default_values: this.defaultValues,
      repetitions: this.repetitions,
      ...(this.defaultValues ? {} : { searched_values: this.parseSearchedValues() })
    };

    localStorage.setItem('generationRequest', JSON.stringify(request));

    this.loading = true;

    this.generationService.generateFragments(request).subscribe({
      next: response => {
        this.result = response;
        this.failedBackends = response.failed_backends ?? []
        localStorage.setItem('generationRequest', JSON.stringify({
          ...request,
          failed_backends: this.failedBackends
        }));
        this.loading = false;
      },

      error: error => {
        this.error =
          error.error?.detail ??
          error.message ??
          'Error generating Grover fragments.';

        this.loading = false;
      }
    });
  }

  isBackendFailed(backend: BackendInfo): boolean {
    return this.failedBackends.some(failed => failed.name === backend.name);
  }

  getBackendFailure(backend: BackendInfo): string {
    return this.failedBackends.find(failed => failed.name === backend.name)?.error ?? '';
  }

  addSearchedValues(): void {
    this.searchedValuesInputs.push('');
    setTimeout(() => this.searchedInputs.last?.nativeElement.focus());
  }

  addSearchedValuesIfLast(index: number): void {
    if (index === this.searchedValuesInputs.length - 1) {
      this.addSearchedValues();
      setTimeout(() => this.searchedInputs.last?.nativeElement.focus());
    }
  }

  removeSearchedValues(index: number): void {
    if (this.searchedValuesInputs.length > 1) {
      this.searchedValuesInputs.splice(index, 1);
    } else {
      this.searchedValuesInputs[0] = '';
    }
  }

  toggleBackend(backend: BackendInfo, checked: boolean): void {
    if (checked) {
      if (!this.isBackendSelected(backend)) {
        this.selectedBackends.push(backend);
      }
    } else {
      this.selectedBackends = this.selectedBackends.filter(value => value.name !== backend.name);
    }
  }

  isBackendSelected(backend: BackendInfo): boolean {
    return this.selectedBackends.some(selected => selected.name === backend.name);
  }

  private parseSearchedValues(): number[][] {
    return this.searchedValuesInputs
      .map(value => this.parseValues(value))
      .filter(values => values.length > 0);
  }

  private parseValues(value: string): number[] {
    if (!value.trim()) {
      return [];
    }

    return value
      .split(',')
      .map(item => item.trim())
      .filter(item => item !== '')
      .map(item => Number(item))
      .filter(item => !Number.isNaN(item));
  }

  loadResults(): void {
    this.resultsLoading = true;
    this.resultsError = '';

    this.generationService.getResults().subscribe({
      next: content => {
        const lines = content
          .trim()
          .split('\n')
          .filter(line => line.trim() !== '');

        if (lines.length === 0) {
          this.resultsHeader = [];
          this.resultsRows = [];
          this.columnFilters = [];
        } else {
          this.resultsHeader = lines[0].split('\t');
          this.resultsRows = lines.slice(1).map(line => line.split('\t'));
          this.columnFilters = new Array(this.resultsHeader.length).fill('');
        }

        this.resultsLoading = false;
      },

      error: error => {
        this.resultsError =
          error.error?.detail ??
          error.message ??
          'Error loading results.';

        this.resultsLoading = false;
      }
    });
  }

  selectAllBackends(): void {
    this.selectedBackends = [...this.availableBackends];
  }
  invertBackendSelection(): void {
    this.selectedBackends = this.availableBackends.filter(backend => !this.isBackendSelected(backend));
  }



  sortColumn = -1;
  sortAscending = true;

  sortResults(columnIndex: number): void {
    if (this.sortColumn === columnIndex) {
      this.sortAscending = !this.sortAscending;
    } else {
      this.sortColumn = columnIndex;
      this.sortAscending = true;
    }

    this.resultsRows.sort((a, b) => {
      const aValue = a[columnIndex] ?? '';
      const bValue = b[columnIndex] ?? '';

      const aNumber = Number(aValue);
      const bNumber = Number(bValue);

      let comparison: number;

      if (!Number.isNaN(aNumber) && !Number.isNaN(bNumber)) {
        comparison = aNumber - bNumber;
      } else {
        comparison = aValue.localeCompare(bValue);
      }

      return this.sortAscending ? comparison : -comparison;
    });
  }

  getSortIndicator(columnIndex: number): string {
    if (this.sortColumn !== columnIndex) {
      return '';
    }

    return this.sortAscending ? '▲' : '▼';
  }


  columnFilters: string[] = [];

  get filteredResultsRows(): string[][] {
    return this.resultsRows.filter(row =>
      this.resultsHeader.every((_, index) => {
        const filter = this.columnFilters[index] ?? '';

        if (!filter) {
          return true;
        }

        return row[index] === filter;
      })
    );
  }

  getColumnValues(columnIndex: number): string[] {
    return [...new Set(
      this.resultsRows
        .map(row => row[columnIndex])
        .filter(value => value !== undefined && value !== '')
    )].sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  }

}