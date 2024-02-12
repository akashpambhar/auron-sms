import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SmsList2Component } from './sms-list2.component';

describe('SmsList2Component', () => {
  let component: SmsList2Component;
  let fixture: ComponentFixture<SmsList2Component>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SmsList2Component]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(SmsList2Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
