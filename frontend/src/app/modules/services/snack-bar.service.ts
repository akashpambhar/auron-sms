import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable({
  providedIn: 'root'
})
export class SnackBarService {

  constructor(private snackBar: MatSnackBar) { }

  public showSnackbar(message: string, action: string = 'Close', duration: number = 10000, maxLength: number = 200): void {
    const truncatedMessage = message.length > maxLength ? message.substring(0, maxLength) + '...' : message;

    this.snackBar.open(truncatedMessage, action, {
      duration: duration,
    });
  }
}
