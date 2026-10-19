import { Component, EventEmitter, Input, Output } from '@angular/core';
import { BackendInfo } from '../models/BackendInfo';
import { FailedBackend } from '../models/FailedBackend';
@Component({
  selector: 'app-backend-selector',
  standalone: true,
  imports: [],
  templateUrl: './backend-selector.component.html',
  styleUrl: './backend-selector.component.css'
})
export class BackendSelectorComponent {
  @Input() availableBackends: BackendInfo[] = [];
  @Input() selectedBackends: BackendInfo[] = [];
  @Input() failedBackends: FailedBackend[] = [];
  @Output() selectedBackendsChange = new EventEmitter<BackendInfo[]>();
  isBackendSelected(backend: BackendInfo): boolean {
    return this.selectedBackends.some(selected => selected.name === backend.name);
  }
  toggleBackend(backend: BackendInfo, checked: boolean): void {
    if (checked) {
      if (!this.isBackendSelected(backend)) {
        this.selectedBackendsChange.emit([...this.selectedBackends, backend]);
      }
    } else {
      this.selectedBackendsChange.emit(this.selectedBackends.filter(selected => selected.name !== backend.name));
    }
  }
  selectAllBackends(): void {
    this.selectedBackendsChange.emit([...this.availableBackends]);
  }
  invertBackendSelection(): void {
    this.selectedBackendsChange.emit(this.availableBackends.filter(backend => !this.isBackendSelected(backend)));
  }
  isBackendFailed(backend: BackendInfo): boolean {
    return this.failedBackends.some(failed => failed.name === backend.name);
  }
  getBackendFailure(backend: BackendInfo): string {
    return this.failedBackends.find(failed => failed.name === backend.name)?.error ?? '';
  }
}