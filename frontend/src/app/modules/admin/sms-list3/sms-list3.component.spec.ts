import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SmsList3Component } from './sms-list3.component';

describe('SmsList3Component', () => {
  let component: SmsList3Component;
  let fixture: ComponentFixture<SmsList3Component>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SmsList3Component]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(SmsList3Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
