import { inject } from '@angular/core';
import { CanActivateChildFn, CanActivateFn, Router } from '@angular/router';
import { AuthService } from 'app/core/auth/auth.service';
import { UserService } from 'app/core/user/user.service';
import { of, switchMap } from 'rxjs';

export const NoAuthGuard: CanActivateFn | CanActivateChildFn = (route, state) => {
    const router: Router = inject(Router);
    const userService: UserService = inject(UserService);

    // Check the authentication status
    return inject(AuthService).check().pipe(
        switchMap((authenticated) => {
            // If the user is authenticated...
            if (authenticated) {
                return userService.user$.pipe(switchMap((user: any) => {
                    if (user.role === 1) {
                        return of(router.parseUrl('admin-dashboard'));
                    } else if (user.role === 2) {
                        return of(router.parseUrl('sms-list'));
                    } else if (user.role === 3) {
                        return of(router.parseUrl('no-access'));
                    }
                }));
            }
            
            return of(true);
        }),
    );
};
