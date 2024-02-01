import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-sms-detail',
  standalone: true,
  imports: [CommonModule, MatButtonModule],
  templateUrl: './sms-detail.component.html',
  styleUrl: './sms-detail.component.scss'
})
export class SmsDetailComponent implements OnInit {

  sms = { ToAddress: '', Body: '', StatusID: 1, SentTime: '' };

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: any,
    public dialogRef: MatDialogRef<SmsDetailComponent>,
  ) { }

  ngOnInit(): void {
    this.sms = this.data;
  }

  exportPDF() {
    
  }

  closeDialog(message?: any) {
    this.dialogRef.close(message);
  }
}
