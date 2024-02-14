import { NgIf } from '@angular/common';
import { Component, OnDestroy, OnInit, ViewEncapsulation } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { ActivatedRoute, Router, RouterOutlet } from '@angular/router';
import { FuseFullscreenComponent } from '@fuse/components/fullscreen';
import { FuseLoadingBarComponent } from '@fuse/components/loading-bar';
import { FuseNavigationItem, FuseNavigationService, FuseVerticalNavigationComponent } from '@fuse/components/navigation';
import { FuseMediaWatcherService } from '@fuse/services/media-watcher';
import { NavigationService } from 'app/core/navigation/navigation.service';
import { Navigation } from 'app/core/navigation/navigation.types';
import { UserService } from 'app/core/user/user.service';
import { User } from 'app/core/user/user.types';



import { SearchComponent } from 'app/layout/common/search/search.component';

import { UserComponent } from 'app/layout/common/user/user.component';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'classy-layout',
  templateUrl: './classy.component.html',
  encapsulation: ViewEncapsulation.None,
  standalone: true,
  imports: [FuseLoadingBarComponent, FuseVerticalNavigationComponent, UserComponent, NgIf, MatIconModule, MatButtonModule, FuseFullscreenComponent, SearchComponent, RouterOutlet],
})
export class ClassyLayoutComponent implements OnInit, OnDestroy {
  isScreenSmall: boolean;
  navigation: Navigation;
  user: User;
  private _unsubscribeAll: Subject<any> = new Subject<any>();
  defaultNavigation: FuseNavigationItem[] = []
  compactNavigation: FuseNavigationItem[] = []
  futuristicNavigation: FuseNavigationItem[] = []
  horizontalNavigation: FuseNavigationItem[] = []


  /**
   * Constructor
   */
  constructor(
    private _activatedRoute: ActivatedRoute,
    private _router: Router,
    private _navigationService: NavigationService,
    private _userService: UserService,
    private _fuseMediaWatcherService: FuseMediaWatcherService,
    private _fuseNavigationService: FuseNavigationService,
  ) {
    this.defaultNavigation = [
      {
        id: 'admin-dashboard',
        title: 'Admin dasboard',
        type: 'basic',
        icon: 'heroicons_outline:computer-desktop',
        link: '/admin-dashboard',
        hidden: () => !(this.user.role == 1)
      },
      {
        id: 'sms-list',
        title: 'SMS List',
        type: 'basic',
        icon: 'heroicons_outline:table-cells',
        link: '/sms-list',
        hidden: () => !(this.user.role == 1 || this.user.role == 2 || this.user.role == 3)
      },
      {
        id: 'sms-list2',
        title: 'SMS List 2',
        type: 'basic',
        icon: 'heroicons_outline:table-cells',
        link: '/sms-list2',
        hidden: () => !(this.user.role == 1 || this.user.role == 2 || this.user.role == 3)
      },
      {
        id: 'sms-list3',
        title: 'SMS List 3',
        type: 'basic',
        icon: 'heroicons_outline:table-cells',
        link: '/sms-list3',
        hidden: () => !(this.user.role == 1 || this.user.role == 2 || this.user.role == 3)
      },
    ];
    this.compactNavigation = [
      {
        id: 'example',
        title: 'Example',
        type: 'basic',
        icon: 'heroicons_outline:chart-pie',
        link: '/example'
      }
    ];
    this.futuristicNavigation = [
      {
        id: 'example',
        title: 'Example',
        type: 'basic',
        icon: 'heroicons_outline:chart-pie',
        link: '/example'
      }
    ];
    this.horizontalNavigation = [
      {
        id: 'example',
        title: 'Example',
        type: 'basic',
        icon: 'heroicons_outline:chart-pie',
        link: '/example'
      }
    ];
  }

  // -----------------------------------------------------------------------------------------------------
  // @ Accessors
  // -----------------------------------------------------------------------------------------------------

  /**
   * Getter for current year
   */
  get currentYear(): number {
    return new Date().getFullYear();
  }

  // -----------------------------------------------------------------------------------------------------
  // @ Lifecycle hooks
  // -----------------------------------------------------------------------------------------------------

  /**
   * On init
   */
  ngOnInit(): void {
    // Subscribe to navigation data
    this._navigationService.navigation$
      .pipe(takeUntil(this._unsubscribeAll))
      .subscribe((navigation: Navigation) => {
        this.navigation = { default: this.defaultNavigation, compact: this.compactNavigation, futuristic: this.futuristicNavigation, horizontal: this.horizontalNavigation };
      });

    // Subscribe to the user service
    this._userService.user$
      .pipe((takeUntil(this._unsubscribeAll)))
      .subscribe((user: User) => {
        this.user = user;
      });

    // Subscribe to media changes
    // this._fuseMediaWatcherService.onMediaChange$
    //   .pipe(takeUntil(this._unsubscribeAll))
    //   .subscribe(({ matchingAliases }) => {
    //     // Check if the screen is small
    //     this.isScreenSmall = !matchingAliases.includes('md');
    //   });
  }

  /**
   * On destroy
   */
  ngOnDestroy(): void {
    // Unsubscribe from all subscriptions
    this._unsubscribeAll.next(null);
    this._unsubscribeAll.complete();
  }

  // -----------------------------------------------------------------------------------------------------
  // @ Public methods
  // -----------------------------------------------------------------------------------------------------

  /**
   * Toggle navigation
   *
   * @param name
   */
  toggleNavigation(name: string): void {
    // Get the navigation
    const navigation = this._fuseNavigationService.getComponent<FuseVerticalNavigationComponent>(name);

    if (navigation) {
      // Toggle the opened status
      navigation.toggle();
    }
  }
}
