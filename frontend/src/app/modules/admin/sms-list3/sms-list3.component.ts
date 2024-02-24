import { Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatPaginatorModule, MatPaginator, PageEvent } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { PageSort } from 'app/modules/models/utils';
import { SnackBarService } from 'app/modules/services/snack-bar.service';
import { SmsDetailComponent } from '../sms-detail/sms-detail.component';
import { saveAs } from 'file-saver';
import { Sms3Service } from 'app/modules/services/sms3.service';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { SelectionModel } from '@angular/cdk/collections';
import { MatCheckboxModule } from '@angular/material/checkbox';

@Component({
  selector: 'app-sms-list3',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatFormFieldModule, FormsModule, MatInputModule,MatCheckboxModule,
    MatPaginatorModule, MatProgressSpinnerModule, MatButtonModule, ReactiveFormsModule, MatDatepickerModule, MatSortModule],
  templateUrl: './sms-list3.component.html',
  styleUrl: './sms-list3.component.scss'
})
export class SmsList3Component {
  displayedColumns: string[] = ['select', 'MessageID', 'ToAddress', 'Body', 'StatusID', 'SentTime'];
  smsList = new MatTableDataSource<any>();
  selection = new SelectionModel<any>(true, []);

  searchTerm = ''

  dateRange = this.fb.group({
    start: [null],
    end: [null],
  });

  pageAndSort: PageSort = {
    page: 0, size: 5, sort: {
      active: "SentTime",
      direction: "desc"
    }
  };

  isLoading = false;

  constructor(
    private fb: FormBuilder,
    private smsService: Sms3Service,
    public dialog: MatDialog,
    private snackBarService: SnackBarService
  ) { }

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;

  ngOnInit(): void {
    this.loadSMS()
  }

  ngAfterViewInit(){
    this.smsList.paginator = this.paginator;
    this.smsList.sort = this.sort;
  }

  loadSMS() {
    this.isLoading = true;
    this.smsService.getAllSMS().subscribe({
      next: (data) => {
        this.smsList.data = data.items;
        this.isLoading = false;
      },
      error: (error) => {
        this.snackBarService.showSnackbar(error.error.detail)
        this.isLoading = false;
      }
    })
  }

  onDateRangeChange() {
  }

  searchSMS() {
    this.isLoading = true;

    this.smsService.searchAllSMSByMobileNumber(this.searchTerm).subscribe({
      next: (data) => {
        console.log("DATA RECEIVED3");
        console.log(data);
        
        this.smsList.data = data.items;
        this.isLoading = false;
      },
      error: (error) => {
        this.snackBarService.showSnackbar(error.error.detail)
        this.isLoading = false;
      }
    })
  }

  exportExcel() {
    if (this.selection.selected.length === 0) {
      this.snackBarService.showSnackbar("Please select any records to export")
      return;
    }
    
    this.smsService.exportExcel(this.smsList.sortData(this.selection.selected, this.sort)).subscribe({
      next: (data) => {
        this.handleFileDownload(data);
      },
      error: (error) => {
        this.snackBarService.showSnackbar(error.error.detail)
      }
    })
  }

  private handleFileDownload(response: any): void {
    const blob = new Blob([response.body], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

    const date = new Date();
    const dateString = date.getFullYear() + "-" +
      ("0" + (date.getMonth() + 1)).slice(-2) + "-" +
      ("0" + date.getDate()).slice(-2) + "_" +
      ("0" + date.getHours()).slice(-2) + "-" +
      ("0" + date.getMinutes()).slice(-2) + "-" +
      ("0" + date.getSeconds()).slice(-2);

    const filename = `auron_sms_${dateString}.xlsx`;
    saveAs(blob, filename);
  }

  resetFilter() {
    this.searchTerm = '';
    this.dateRange.reset();
    this.resetPageSort();
    this.loadSMS();
    this.selection.clear();
  }

  resetPageSort() {
    this.paginator.pageIndex = 0;
    this.paginator.pageSize = 5;
    this.pageAndSort = {
      page: 0, size: 5, sort: {
        active: "SentTime",
        direction: "desc"
      }
    };
  }

  nextPage(event: PageEvent) {
    this.pageAndSort.page = event.pageIndex;
    this.pageAndSort.size = event.pageSize;

    if (this.searchTerm)
      this.searchSMS();
    else
      this.loadSMS();
  }

  openDialog(data: any) {
    this.dialog.open(SmsDetailComponent, {
      data: data
    })
  }

  /** Whether the number of selected elements matches the total number of rows. */
  isAllSelected() {
    const numSelected = this.selection.selected.length;
    const numRows = this.smsList.data.length;
    return numSelected === numRows;
  }

  /** Selects all rows if they are not all selected; otherwise clear selection. */
   masterToggle() {
    if (this.isAllSelected()) {
      this.selection.clear()
    }
    else {
      this.selection.clear()
      this.smsList.data.forEach(row => this.selection.select(row));
    }
  }

  checkboxLabel(row?: any): string {
    if (!row) {
      return `${this.isAllSelected() ? 'select' : 'deselect'} all`;
    }
    return `${this.selection.isSelected(row) ? 'deselect' : 'select'} row ${row.id}`;
  }
}
