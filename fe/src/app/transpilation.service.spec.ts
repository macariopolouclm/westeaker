import { TestBed } from '@angular/core/testing';

import { TranspilationService } from './transpilation.service';

describe('TranspilationService', () => {
  let service: TranspilationService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TranspilationService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
