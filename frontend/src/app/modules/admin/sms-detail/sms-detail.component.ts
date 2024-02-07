import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { SmsService } from 'app/modules/services/sms.service';
import { saveAs } from 'file-saver';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-sms-detail',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatProgressSpinnerModule],
  templateUrl: './sms-detail.component.html',
  styleUrl: './sms-detail.component.scss'
})
export class SmsDetailComponent implements OnInit {

  sms = { MessageID: '', ToAddress: '', Body: '', StatusID: 1, SentTime: '' };
  isLoading = false;

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: any,
    public dialogRef: MatDialogRef<SmsDetailComponent>,
    private smsService: SmsService
  ) { }

  ngOnInit(): void {
    this.sms = this.data;
  }

  exportPDF() {
    this.isLoading = true;
  
    this.smsService.exportPDF(this.sms).subscribe((res: any) => {
      this.handleFileDownload(res)
    })
  }

  private handleFileDownload(response: any): void {
    const blob = new Blob([response.body], { type: 'application/pdf' });
    saveAs(blob);
    this.isLoading = false;
  }

  closeDialog(message?: any) {
    this.dialogRef.close(message);
  }
}
