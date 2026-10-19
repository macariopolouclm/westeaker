import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BackendSelectorComponent } from './backend-selector.component';

describe('BackendSelectorComponent', () => {
  let component: BackendSelectorComponent;
  let fixture: ComponentFixture<BackendSelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BackendSelectorComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BackendSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
