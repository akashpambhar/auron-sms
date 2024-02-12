import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable({
  providedIn: 'root'
})
export class SnackBarService {

  constructor(private snackBar: MatSnackBar) { }

  public showSnackbar(message: string, action: string = 'Close', duration: number = 10000): void {
    this.snackBar.open(message, action, {
      duration: duration,
    });
  }
}
