import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TranspilationComponent } from './transpilation.component';

describe('TranspilationComponent', () => {
  let component: TranspilationComponent;
  let fixture: ComponentFixture<TranspilationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TranspilationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TranspilationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
