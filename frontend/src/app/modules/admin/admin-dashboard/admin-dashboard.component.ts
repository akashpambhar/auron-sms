import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatRadioModule } from '@angular/material/radio';
import { UserUpdateComponent } from '../user-update/user-update.component';
import { MatDialog } from '@angular/material/dialog';
import { UserService } from 'app/modules/services/user.service';
import { SnackBarService } from 'app/modules/services/snack-bar.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatFormFieldModule, FormsModule, MatInputModule,
    MatPaginatorModule, MatProgressSpinnerModule, MatButtonModule, ReactiveFormsModule, MatSelectModule, MatRadioModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrl: './admin-dashboard.component.scss'
})
export class AdminDashboardComponent implements OnInit {
  displayedColumns: string[] = ['username', 'email', 'disabled', 'role_name', 'actions'];
  UserList = new MatTableDataSource<any>();

  searchTerm = ''
  isLoading : boolean

  constructor(
    public dialog: MatDialog,
    private userService: UserService,
    private snackBarService: SnackBarService
  ) {
  }
  ngOnInit(): void {
    this.loadUsers()
  }

  loadUsers() {
    this.isLoading = true;
    this.userService.getAllUser().subscribe((data) => {
      this.UserList = data
      this.isLoading = false;
    })
  }

  searchSMS() {
    if (this.searchTerm !== "") {
      this.isLoading = true;
      this.userService.getByUsername(this.searchTerm).subscribe((user: any) => {
        this.UserList = user
        this.isLoading = false;
      })
    }
    else{
      this.loadUsers()
    }
  }

  resetFilter() {
    this.searchTerm = '';
  }

  updateUser(userId: any) {
    this.openDialog(userId)
  }

  deleteUser(userId: any) {
    let confirmation = confirm("Are you sure you want to delete this user?");

    if (confirmation) {
      this.userService.deleteById(userId).subscribe((res: any) => {
        this.snackBarService.showSnackbar(res)
        this.loadUsers()
      })
    }
  }

  openDialog(userId?: number) {
    const dialogRef = this.dialog.open(UserUpdateComponent, {
      data: {
        userId: userId
      }
    })

    dialogRef.afterClosed().subscribe((res: any) => {
      if (res == true) {
        this.loadUsers()
      }
    })
  }
}
