import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { UserService } from 'src/app/services/user.service';
import { User } from 'src/app/shared/models/user';

const USER_KEY = 'isLoggedIn'; // Use the same key for consistency
const USER_DETAILS = 'loggedUser'

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit {
  static user: User;
  static static_user_name:String="";
  constructor(private userService: UserService,private router:Router) {
    
  }

  ngOnInit(): void {
    HeaderComponent.updateHeaderName()
  }

  static updateHeaderName(){
    if (localStorage.getItem(USER_KEY)) {
      const userData: string | null = localStorage.getItem(USER_DETAILS);
      if (userData) {
        HeaderComponent.user = JSON.parse(userData);
        HeaderComponent.static_user_name = HeaderComponent.user.name;
      }
    }
  }

  get staticName() {
    return HeaderComponent.static_user_name;
  }

  logout(){
    this.userService.logout();
  }

  //get
  isAuth(){
    // indicates whether the user has logged in (true), or logged out(false)
    //return this.userService.isLoggedIn();
    if(localStorage.getItem(USER_KEY))
      return true;
    return false;
  }
}
