import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { PageSort } from 'app/modules/models/utils';
import { AuthService } from 'app/core/auth/auth.service';
import { UserService } from 'app/modules/services/user.service';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { SnackBarService } from 'app/modules/services/snack-bar.service';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-audit-trail',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatPaginatorModule, MatProgressSpinnerModule, MatSortModule],
  templateUrl: './audit-trail.component.html',
  styleUrl: './audit-trail.component.scss'
})
export class AuditTrailComponent implements OnInit{
  displayedColumns: string[] = ['audit_trail_id', 'username', 'ip_address', 'action', 'method', 'query_params', 'auth_mode', 'timestamp'];
  auditTrailList = new MatTableDataSource<any>();

  pageAndSort: PageSort = {
    page: 0, size: 5, sort: {
      active: "SentTime",
      direction: "desc"
    }
  };

  isLoading = false;

  constructor(
    private smsService: UserService,
    private snackBarService: SnackBarService
  ) { }

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;

  ngOnInit(): void {
    this.loadAuditTrail();
  }

  ngAfterViewInit() {
    this.auditTrailList.paginator = this.paginator;
    this.auditTrailList.sort = this.sort;
  }

  loadAuditTrail() {
    this.isLoading = true;
    this.smsService.getAuditTrails().subscribe({
      next: (data) => {
        this.auditTrailList.data = data;
        console.log(data);
        
        this.isLoading = false;
      },
      error: (error) => {
        this.snackBarService.showSnackbar(error.error.detail)
        this.isLoading = false;
      }
    })
  }
}
